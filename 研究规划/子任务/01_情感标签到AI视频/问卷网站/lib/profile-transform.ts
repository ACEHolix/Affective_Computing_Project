import { SurveyAnswers } from "./survey-schema";
import { buildFiveStagePrompts } from "./prompt-transform";

type StringArray = string[];

function asStringArray(value: unknown): StringArray {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}

function asRecord(value: unknown): Record<string, number> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return {};
  }
  return Object.fromEntries(
    Object.entries(value).filter(([, item]) => typeof item === "number"),
  ) as Record<string, number>;
}

function buildConstraintProfile(answers: SurveyAnswers) {
  return {
    themeBlacklist: asStringArray(answers.theme_blacklist),
    narrativeThemeBlacklist: asStringArray(answers.narrative_theme_blacklist),
    maxEmotionIntensity: asNumber(answers.max_emotion_intensity),
    stimulusToleranceProfile: asRecord(answers.stimulus_tolerance_profile),
  };
}

function buildPreferenceProfile(answers: SurveyAnswers) {
  return {
    sceneTypes: asStringArray(answers.preferred_scene_types),
    narrativeThemes: asStringArray(answers.preferred_narrative_themes),
    visualStyles: asStringArray(answers.preferred_visual_styles),
    colorLighting: asStringArray(answers.preferred_color_lighting),
    audioElements: asStringArray(answers.preferred_audio_elements),
    pacingMode: asString(answers.preferred_pacing_mode),
    baselinePacingPreference: asString(answers.baseline_pacing_preference),
  };
}

function buildSelfRelevanceProfile(answers: SurveyAnswers) {
  return {
    selfRelevantScenes: asStringArray(answers.self_relevant_scenes),
    highIntensityThemes: asStringArray(answers.high_intensity_themes),
    autobiographicalCues: asStringArray(answers.autobiographical_cues),
    freeformEmotionalKeywords: asString(answers.freeform_emotional_keywords)
      .split(/[\n,，、;；]+/)
      .map((item) => item.trim())
      .filter(Boolean),
  };
}

function buildEmotionGoalProfile(answers: SurveyAnswers) {
  return {
    targetEmotionIntensityProfile: asRecord(answers.target_emotion_intensity_profile),
    emotionInductionMode: asString(answers.emotion_induction_mode),
    negativePhasePreference: asString(answers.negative_phase_preference),
  };
}

function buildBackgroundProfile(answers: SurveyAnswers) {
  return {
    ageGroup: asString(answers.age_group),
    gender: asString(answers.gender),
    contentFormatFamiliarity: asStringArray(answers.content_format_familiarity),
  };
}

export function transformAnswersToProfile(answers: SurveyAnswers) {
  const background = buildBackgroundProfile(answers);
  const constraints = buildConstraintProfile(answers);
  const preferences = buildPreferenceProfile(answers);
  const selfRelevance = buildSelfRelevanceProfile(answers);
  const emotionGoals = buildEmotionGoalProfile(answers);

  const result = {
    surveyVersion: "2026-04-01",
    profile: {
      background,
      constraints,
      preferences,
      selfRelevance,
      emotionGoals,
    },
    generationInputs: {
      blacklist: [...constraints.themeBlacklist, ...constraints.narrativeThemeBlacklist],
      dominantScenes: preferences.sceneTypes.slice(0, 3),
      dominantThemes: preferences.narrativeThemes.slice(0, 3),
      dominantVisualStyles: preferences.visualStyles.slice(0, 3),
      dominantAudioElements: preferences.audioElements.slice(0, 3),
      personalCues: [
        ...selfRelevance.selfRelevantScenes.slice(0, 3),
        ...selfRelevance.autobiographicalCues.slice(0, 3),
        ...selfRelevance.freeformEmotionalKeywords.slice(0, 4),
      ],
      pacingMode: preferences.pacingMode,
      emotionInductionMode: emotionGoals.emotionInductionMode,
      negativePhasePreference: emotionGoals.negativePhasePreference,
      maxEmotionIntensity: constraints.maxEmotionIntensity,
    },
  };

  return {
    ...result,
    promptPackage: buildFiveStagePrompts(result.generationInputs),
  };
}
