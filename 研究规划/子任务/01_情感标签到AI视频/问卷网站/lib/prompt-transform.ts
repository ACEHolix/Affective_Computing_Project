type GenerationInputs = {
  blacklist: string[];
  dominantScenes: string[];
  dominantThemes: string[];
  dominantVisualStyles: string[];
  dominantAudioElements: string[];
  personalCues: string[];
  pacingMode: string;
  emotionInductionMode: string;
  negativePhasePreference: string;
  maxEmotionIntensity: number | null;
};

type StageDefinition = {
  id: string;
  label: string;
  goal: string;
  mood: string;
  motion: string;
  specialFocus: string[];
};

function humanize(values: string[]) {
  if (values.length === 0) {
    return "neutral generic elements";
  }
  return values.join(", ");
}

function buildAvoidClause(blacklist: string[]) {
  if (blacklist.length === 0) {
    return "avoid abrupt unrelated elements";
  }
  return `avoid ${blacklist.join(", ")}`;
}

function stageDefinitions(inputs: GenerationInputs): StageDefinition[] {
  const negativeModeMap: Record<string, string> = {
    low_arousal_negative: "melancholy, quiet loss, emotional distance",
    medium_arousal_negative: "pressure, uncertainty, restrained anxiety",
    high_arousal_negative: "fear, strong tension, escalating threat",
    avoid_negative: "very mild negative shading only, keep emotional safety",
  };

  return [
    {
      id: "stage_1",
      label: "Stage 1 / Positive Activation",
      goal: "move from neutral toward positive high-arousal activation",
      mood: "uplifting, anticipatory, energizing",
      motion: inputs.pacingMode === "slow_long_take" ? "slow build with rising energy" : "clear increasing momentum",
      specialFocus: [...inputs.dominantScenes.slice(0, 2), ...inputs.dominantThemes.slice(0, 1)],
    },
    {
      id: "stage_2",
      label: "Stage 2 / Positive Softening",
      goal: "keep valence positive while lowering arousal",
      mood: "warm, safe, satisfied, emotionally open",
      motion: "reduce tension and soften pacing",
      specialFocus: [...inputs.dominantScenes.slice(0, 2), ...inputs.personalCues.slice(0, 1)],
    },
    {
      id: "stage_3",
      label: "Stage 3 / Low-Arousal Negative Shift",
      goal: "shift from positive into low-arousal negative emotion",
      mood: negativeModeMap[inputs.negativePhasePreference] ?? negativeModeMap.low_arousal_negative,
      motion: "minimal conflict burst, restrained movement, sparse emotional pressure",
      specialFocus: [...inputs.dominantThemes.slice(0, 2), ...inputs.personalCues.slice(0, 2)],
    },
    {
      id: "stage_4",
      label: "Stage 4 / Negative Escalation",
      goal: "keep negative valence and raise arousal",
      mood: "increasing tension, pressure, uncertainty",
      motion: "tighten framing and intensify sensory pressure without losing coherence",
      specialFocus: [...inputs.dominantThemes.slice(0, 2), ...inputs.dominantAudioElements.slice(0, 1)],
    },
    {
      id: "stage_5",
      label: "Stage 5 / Recovery",
      goal: "move from negative high-arousal toward near-neutral recovery",
      mood: "de-escalation, emotional release, calm return",
      motion: "stabilize camera, reduce density, allow breathing room",
      specialFocus: [...inputs.dominantScenes.slice(0, 2), ...inputs.personalCues.slice(0, 2)],
    },
  ];
}

function buildStagePrompt(stage: StageDefinition, inputs: GenerationInputs) {
  return [
    `Stage goal: ${stage.goal}.`,
    `Scene focus: ${humanize(stage.specialFocus)}.`,
    `Mood: ${stage.mood}.`,
    `Visual style: ${humanize(inputs.dominantVisualStyles)}.`,
    `Audio style: ${humanize(inputs.dominantAudioElements)}.`,
    `Camera and pacing: ${stage.motion}.`,
    `Personal cues: ${humanize(inputs.personalCues.slice(0, 3))}.`,
    `Intensity cap: ${inputs.maxEmotionIntensity ?? "unspecified"} / 5.`,
    `${buildAvoidClause(inputs.blacklist)}.`,
  ].join(" ");
}

export function buildFiveStagePrompts(inputs: GenerationInputs) {
  const stages = stageDefinitions(inputs).map((stage) => ({
    id: stage.id,
    label: stage.label,
    prompt: buildStagePrompt(stage, inputs),
  }));

  return {
    promptVersion: "2026-04-01",
    globalStyleGuide: {
      dominantScenes: inputs.dominantScenes,
      dominantThemes: inputs.dominantThemes,
      dominantVisualStyles: inputs.dominantVisualStyles,
      dominantAudioElements: inputs.dominantAudioElements,
      personalCues: inputs.personalCues,
      blacklist: inputs.blacklist,
      pacingMode: inputs.pacingMode,
      emotionInductionMode: inputs.emotionInductionMode,
      negativePhasePreference: inputs.negativePhasePreference,
      maxEmotionIntensity: inputs.maxEmotionIntensity,
    },
    stages,
  };
}
