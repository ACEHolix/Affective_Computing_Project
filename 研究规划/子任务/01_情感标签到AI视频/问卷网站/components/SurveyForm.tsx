"use client";

import { useMemo, useState } from "react";
import { Section, SurveyAnswers, sections } from "../lib/survey-schema";

const STORAGE_KEY = "subtask01_survey_answers";

function loadStoredAnswers(): SurveyAnswers {
  if (typeof window === "undefined") {
    return {};
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return {};
  }
  try {
    return JSON.parse(raw) as SurveyAnswers;
  } catch {
    return {};
  }
}

function saveStoredAnswers(answers: SurveyAnswers) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
}

export function SurveyForm() {
  const [currentSection, setCurrentSection] = useState(0);
  const [answers, setAnswers] = useState<SurveyAnswers>(() => loadStoredAnswers());
  const [error, setError] = useState<string>("");
  const [submittedJson, setSubmittedJson] = useState<string>("");
  const [profileJson, setProfileJson] = useState<string>("");
  const [promptJson, setPromptJson] = useState<string>("");
  const [savedPath, setSavedPath] = useState<string>("");

  const section = sections[currentSection];
  const progress = ((currentSection + 1) / sections.length) * 100;

  const completion = useMemo(
    () =>
      sections.map((item) => ({
        id: item.id,
        done: item.questions.every((question) => !question.required || isAnswered(answers[question.id])),
      })),
    [answers],
  );

  function updateAnswer(questionId: string, value: unknown) {
    const next = { ...answers, [questionId]: value };
    setAnswers(next);
    saveStoredAnswers(next);
  }

  function validateSection(current: Section) {
    const missing = current.questions.find((question) => question.required && !isAnswered(answers[question.id]));
    if (missing) {
      setError(`请先完成：${missing.title}`);
      return false;
    }
    setError("");
    return true;
  }

  function goNext() {
    if (!validateSection(section)) {
      return;
    }
    setCurrentSection((prev) => Math.min(prev + 1, sections.length - 1));
  }

  function goPrev() {
    setError("");
    setCurrentSection((prev) => Math.max(prev - 1, 0));
  }

  async function handleSubmit() {
    for (const item of sections) {
      const missing = item.questions.find((question) => question.required && !isAnswered(answers[question.id]));
      if (missing) {
        setError(`提交前仍有未完成题目：${missing.title}`);
        return;
      }
    }

    const payload = {
      submittedAt: new Date().toISOString(),
      surveyVersion: "2026-04-01",
      answers,
    };

    const json = JSON.stringify(payload, null, 2);
    setSubmittedJson(json);
    saveStoredAnswers(answers);

    try {
      const response = await fetch("/api/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ answers }),
      });
      if (response.ok) {
        const result = await response.json();
        setSavedPath(result.savedTo ?? "");
        setProfileJson(JSON.stringify(result.transformed?.profile ?? result.transformed, null, 2));
        setPromptJson(JSON.stringify(result.transformed?.promptPackage ?? {}, null, 2));
      }
    } catch {
      setProfileJson("");
      setPromptJson("");
      setSavedPath("");
    }

    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "survey-response.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="survey-layout">
      <aside className="panel sidebar">
        <p className="note">正式版用户画像问卷</p>
        <h2>填写进度</h2>
        <div className="progress" aria-hidden="true">
          <span style={{ width: `${progress}%` }} />
        </div>
        <ol className="step-list">
          {sections.map((item, index) => {
            const active = currentSection === index;
            const done = completion[index]?.done;
            return (
              <li key={item.id} className={active ? "active" : done ? "done" : ""}>
                <strong>{item.title}</strong>
                <div className="note">{item.description}</div>
              </li>
            );
          })}
        </ol>
      </aside>

      <section className="panel">
        <p className="note">
          模块 {currentSection + 1} / {sections.length}
        </p>
        <h1>{section.title}</h1>
        <p className="lead">{section.description}</p>

        {section.questions.map((question) => (
          <div className="question-card" key={question.id}>
            <div className="question-title">{question.title}</div>
            {question.help ? <div className="question-help">{question.help}</div> : null}
            <QuestionField question={question} value={answers[question.id]} onChange={(value) => updateAnswer(question.id, value)} />
          </div>
        ))}

        {error ? <div className="warning">{error}</div> : null}

        <div className="action-row">
          <button type="button" className="secondary" onClick={goPrev} disabled={currentSection === 0}>
            上一步
          </button>
          {currentSection < sections.length - 1 ? (
            <button type="button" onClick={goNext}>
              下一步
            </button>
          ) : (
            <button type="button" onClick={handleSubmit}>
              提交并导出 JSON
            </button>
          )}
        </div>

        {submittedJson ? (
          <div style={{ marginTop: 28 }}>
            <h3>最近一次提交结果</h3>
            <pre className="code-block">{submittedJson}</pre>
          </div>
        ) : null}

        {profileJson ? (
          <div style={{ marginTop: 28 }}>
            <h3>转换后的用户画像 JSON</h3>
            <pre className="code-block">{profileJson}</pre>
          </div>
        ) : null}

        {promptJson ? (
          <div style={{ marginTop: 28 }}>
            <h3>五阶段 Prompt Package</h3>
            <pre className="code-block">{promptJson}</pre>
          </div>
        ) : null}

        {savedPath ? (
          <div style={{ marginTop: 16 }} className="note">
            服务器端已保存提交结果：{savedPath}
          </div>
        ) : null}
      </section>
    </div>
  );
}

function QuestionField({
  question,
  value,
  onChange,
}: {
  question: Section["questions"][number];
  value: unknown;
  onChange: (value: unknown) => void;
}) {
  switch (question.type) {
    case "single_select":
      return (
        <div className="choice-group">
          {question.options?.map((option) => (
            <label className="choice" key={option.value}>
              <input
                type="radio"
                name={question.id}
                checked={value === option.value}
                onChange={() => onChange(option.value)}
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
      );
    case "multi_select": {
      const selected = Array.isArray(value) ? (value as string[]) : [];
      return (
        <>
          <div className="choice-group">
            {question.options?.map((option) => {
              const checked = selected.includes(option.value);
              return (
                <label className="choice" key={option.value}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => {
                      const next = checked
                        ? selected.filter((item) => item !== option.value)
                        : [...selected, option.value];
                      if (question.maxSelect && next.length > question.maxSelect) {
                        return;
                      }
                      onChange(next);
                    }}
                  />
                  <span>{option.label}</span>
                </label>
              );
            })}
          </div>
          {question.maxSelect ? <div className="note">最多选择 {question.maxSelect} 项。</div> : null}
        </>
      );
    }
    case "rating":
      return (
        <div className="rating-row">
          {question.scale?.map((score) => (
            <label className="choice" key={score}>
              <input
                type="radio"
                name={question.id}
                checked={value === score}
                onChange={() => onChange(score)}
              />
              <span>{score}</span>
            </label>
          ))}
        </div>
      );
    case "matrix_rating": {
      const matrix = typeof value === "object" && value !== null ? (value as Record<string, number>) : {};
      return (
        <table className="matrix-table">
          <thead>
            <tr>
              <th>项目</th>
              {question.scale?.map((score) => (
                <th key={score}>{score}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {question.rows?.map((row) => (
              <tr key={row}>
                <td>{row}</td>
                {question.scale?.map((score) => (
                  <td key={`${row}-${score}`}>
                    <input
                      type="radio"
                      name={`${question.id}-${row}`}
                      checked={matrix[row] === score}
                      onChange={() => onChange({ ...matrix, [row]: score })}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }
    case "text_short":
      return (
        <input
          className="text-input"
          type="text"
          value={typeof value === "string" ? value : ""}
          onChange={(event) => onChange(event.target.value)}
        />
      );
    case "text_long":
      return (
        <textarea
          className="textarea"
          rows={5}
          value={typeof value === "string" ? value : ""}
          onChange={(event) => onChange(event.target.value)}
        />
      );
    default:
      return null;
  }
}

function isAnswered(value: unknown) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  if (typeof value === "object" && value !== null) {
    return Object.keys(value).length > 0;
  }
  if (typeof value === "string") {
    return value.trim().length > 0;
  }
  return value !== undefined && value !== null;
}
