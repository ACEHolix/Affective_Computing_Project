export type QuestionType =
  | "single_select"
  | "multi_select"
  | "rating"
  | "matrix_rating"
  | "text_short"
  | "text_long";

export type Option = {
  value: string;
  label: string;
};

export type Question = {
  id: string;
  title: string;
  help?: string;
  type: QuestionType;
  required?: boolean;
  maxSelect?: number;
  options?: Option[];
  scale?: number[];
  rows?: string[];
};

export type Section = {
  id: string;
  title: string;
  description: string;
  questions: Question[];
};

export const sections: Section[] = [
  {
    id: "basic",
    title: "基本信息与媒介经验",
    description: "用于冷启动修正和媒介形式适配，不作为内容决定变量单独使用。",
    questions: [
      {
        id: "age_group",
        title: "Q1. 您的年龄段是？",
        type: "single_select",
        required: true,
        options: [
          { value: "under_18", label: "18 岁以下" },
          { value: "18_25", label: "18 到 25 岁" },
          { value: "26_35", label: "26 到 35 岁" },
          { value: "36_45", label: "36 到 45 岁" },
          { value: "46_60", label: "46 到 60 岁" },
          { value: "over_60", label: "60 岁以上" },
        ],
      },
      {
        id: "gender",
        title: "Q2. 您的性别是？",
        type: "single_select",
        required: true,
        options: [
          { value: "female", label: "女性" },
          { value: "male", label: "男性" },
          { value: "non_binary_or_unspecified", label: "非二元 / 不便说明" },
        ],
      },
      {
        id: "content_format_familiarity",
        title: "Q3. 您平时最常接触的视频内容形式是？",
        type: "multi_select",
        required: true,
        maxSelect: 4,
        options: [
          { value: "short_video", label: "短视频" },
          { value: "film", label: "电影" },
          { value: "series", label: "剧集" },
          { value: "animation", label: "动画" },
          { value: "mv", label: "MV" },
          { value: "game_video", label: "游戏视频" },
          { value: "vr", label: "VR / 360 视频" },
        ],
      },
      {
        id: "baseline_pacing_preference",
        title: "Q4. 您更习惯哪种视频节奏？",
        type: "single_select",
        required: true,
        options: [
          { value: "very_slow", label: "很慢" },
          { value: "slow", label: "偏慢" },
          { value: "medium", label: "中等" },
          { value: "fast", label: "偏快" },
          { value: "very_fast", label: "很快" },
        ],
      },
    ],
  },
  {
    id: "safety",
    title: "风险边界与刺激容忍度",
    description: "这部分会直接决定黑名单和刺激强度上限。",
    questions: [
      {
        id: "theme_blacklist",
        title: "Q5. 以下哪些内容必须避免出现在视频中？",
        type: "multi_select",
        required: true,
        options: [
          { value: "violence", label: "暴力" },
          { value: "gore", label: "血腥" },
          { value: "death", label: "死亡" },
          { value: "medical", label: "医疗场景" },
          { value: "family_conflict", label: "家庭冲突" },
          { value: "crowd", label: "拥挤人群" },
          { value: "confined_space", label: "密闭空间" },
          { value: "dark_space", label: "黑暗空间" },
          { value: "flash", label: "快速闪烁" },
          { value: "sharp_noise", label: "尖锐噪声" },
          { value: "falling_or_chase", label: "追逐 / 坠落" },
        ],
      },
      {
        id: "max_emotion_intensity",
        title: "Q6. 您可接受的整体情绪刺激强度上限是多少？",
        type: "rating",
        required: true,
        scale: [1, 2, 3, 4, 5],
      },
      {
        id: "stimulus_tolerance_profile",
        title: "Q7. 您对以下刺激元素的耐受度如何？",
        type: "matrix_rating",
        required: true,
        rows: ["快速剪辑", "大音量", "低频压迫音", "画面抖动", "黑暗环境", "强冲突叙事"],
        scale: [1, 2, 3, 4, 5],
      },
    ],
  },
  {
    id: "themes",
    title: "内容主题偏好",
    description: "用于决定场景池、叙事母题和黑名单。",
    questions: [
      {
        id: "preferred_scene_types",
        title: "Q8. 以下哪些场景最容易吸引您？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "seaside", label: "海边" },
          { value: "forest", label: "山林" },
          { value: "rainy_street", label: "雨夜街道" },
          { value: "sunset_city", label: "黄昏城市" },
          { value: "home_space", label: "家庭空间" },
          { value: "campus", label: "校园" },
          { value: "road_trip", label: "公路旅行" },
          { value: "cafe", label: "咖啡馆" },
          { value: "empty_room", label: "空旷房间" },
          { value: "memory_scene", label: "旧时回忆场景" },
          { value: "fantasy_world", label: "幻想世界" },
          { value: "sci_fi_city", label: "科幻城市" },
        ],
      },
      {
        id: "preferred_narrative_themes",
        title: "Q9. 以下哪些叙事主题最容易打动您？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "reunion", label: "重逢" },
          { value: "companionship", label: "陪伴" },
          { value: "growth", label: "成长" },
          { value: "farewell", label: "离别" },
          { value: "being_understood", label: "被理解" },
          { value: "missed_chance", label: "错过" },
          { value: "self_healing", label: "自我疗愈" },
          { value: "adventure", label: "冒险" },
          { value: "achievement", label: "成就" },
          { value: "hope", label: "希望" },
          { value: "loneliness", label: "孤独" },
          { value: "belonging", label: "归属感" },
        ],
      },
      {
        id: "narrative_theme_blacklist",
        title: "Q10. 以下哪些主题虽然能引发情绪，但您不希望视频使用？",
        type: "multi_select",
        required: false,
        options: [
          { value: "farewell", label: "离别" },
          { value: "illness", label: "疾病" },
          { value: "family_conflict", label: "家庭冲突" },
          { value: "failure", label: "失败" },
          { value: "shame", label: "羞耻" },
          { value: "violence_threat", label: "暴力威胁" },
          { value: "isolation", label: "孤立感" },
        ],
      },
    ],
  },
  {
    id: "style",
    title: "视听风格偏好",
    description: "用于控制风格、光照、镜头节奏和声音层。",
    questions: [
      {
        id: "preferred_visual_styles",
        title: "Q11. 您偏好的视觉风格是？",
        type: "multi_select",
        required: true,
        maxSelect: 4,
        options: [
          { value: "cinematic", label: "写实电影感" },
          { value: "dreamy_soft", label: "梦幻柔和" },
          { value: "nostalgic", label: "复古怀旧" },
          { value: "animation", label: "动画风" },
          { value: "minimal", label: "极简风" },
          { value: "futuristic", label: "未来感" },
          { value: "slice_of_life", label: "生活流" },
          { value: "documentary", label: "纪录片感" },
        ],
      },
      {
        id: "preferred_color_lighting",
        title: "Q12. 您偏好的色彩和光照是？",
        type: "multi_select",
        required: true,
        maxSelect: 4,
        options: [
          { value: "warm", label: "暖色" },
          { value: "cool", label: "冷色" },
          { value: "high_saturation", label: "高饱和" },
          { value: "low_saturation", label: "低饱和" },
          { value: "soft_diffuse", label: "柔和散射光" },
          { value: "high_contrast", label: "强对比光影" },
          { value: "daylight", label: "白天自然光" },
          { value: "dusk", label: "黄昏暮色" },
          { value: "neon_night", label: "夜景霓虹" },
        ],
      },
      {
        id: "preferred_audio_elements",
        title: "Q13. 以下哪些声音元素最容易让您进入情绪状态？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "piano", label: "钢琴" },
          { value: "strings", label: "弦乐" },
          { value: "electronic_ambient", label: "电子氛围" },
          { value: "humming_voice", label: "人声哼唱" },
          { value: "nature_ambience", label: "自然环境音" },
          { value: "rain", label: "雨声" },
          { value: "waves", label: "海浪声" },
          { value: "city_ambience", label: "城市场景声" },
          { value: "low_frequency_tension", label: "低频张力音" },
        ],
      },
      {
        id: "preferred_pacing_mode",
        title: "Q14. 如果必须选一种镜头节奏，您更偏好哪一种？",
        type: "single_select",
        required: true,
        options: [
          { value: "slow_long_take", label: "长镜头缓慢推进" },
          { value: "moderate_cut", label: "中等节奏切换" },
          { value: "fast_cut", label: "快节奏剪辑" },
        ],
      },
    ],
  },
  {
    id: "self_relevance",
    title: "自我相关线索",
    description: "高价值字段，用于提升情绪穿透力和个体化命中率。",
    questions: [
      {
        id: "self_relevant_scenes",
        title: "Q15. 以下哪些场景对您有明显的个人意义？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "home", label: "家" },
          { value: "school", label: "学校" },
          { value: "seaside", label: "海边" },
          { value: "rainy_street", label: "雨天街道" },
          { value: "late_night_room", label: "深夜房间" },
          { value: "mountain_road", label: "山路" },
          { value: "station", label: "车站" },
          { value: "transport", label: "交通工具" },
          { value: "indoor_space", label: "某类室内空间" },
        ],
      },
      {
        id: "high_intensity_themes",
        title: "Q16. 以下哪些主题最容易引发您的强烈情绪变化？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "companionship", label: "陪伴" },
          { value: "reunion", label: "重逢" },
          { value: "farewell", label: "离别" },
          { value: "being_understood", label: "被理解" },
          { value: "being_ignored", label: "被忽视" },
          { value: "missed_chance", label: "错过" },
          { value: "achievement", label: "成就" },
          { value: "failure", label: "失败" },
          { value: "safety", label: "安全感" },
          { value: "loneliness", label: "孤独" },
        ],
      },
      {
        id: "autobiographical_cues",
        title: "Q17. 以下哪些元素最容易让您联想到个人经历？",
        type: "multi_select",
        required: true,
        maxSelect: 5,
        options: [
          { value: "rain_sound", label: "雨声" },
          { value: "sea_wind", label: "海风" },
          { value: "sunset", label: "黄昏" },
          { value: "night_light", label: "夜灯" },
          { value: "specific_color", label: "某种颜色" },
          { value: "room_layout", label: "某种房间布局" },
          { value: "transport_context", label: "某种交通环境" },
          { value: "old_photo_texture", label: "旧照片感" },
          { value: "music_texture", label: "某种音乐质感" },
        ],
      },
      {
        id: "freeform_emotional_keywords",
        title: "Q18. 请用 3 到 5 个关键词描述“最能打动你的画面或情境”。",
        help: "这里允许少量开放文本，后续会用于人工编码或 LLM 辅助提取。",
        type: "text_long",
        required: false,
      },
    ],
  },
  {
    id: "emotion",
    title: "目标情绪与诱发方式偏好",
    description: "用于控制阶段强度、诱发方式和负向阶段类型。",
    questions: [
      {
        id: "target_emotion_intensity_profile",
        title: "Q19. 对以下目标情绪，您希望视频诱发的强度是多少？",
        type: "matrix_rating",
        required: true,
        rows: ["快乐", "平静", "感动", "兴奋", "紧张", "悲伤"],
        scale: [1, 2, 3, 4, 5],
      },
      {
        id: "emotion_induction_mode",
        title: "Q20. 如果目标是诱发某种情绪，您更偏好哪种方式？",
        type: "single_select",
        required: true,
        options: [
          { value: "direct", label: "直接强刺激" },
          { value: "build_up", label: "缓慢铺垫后增强" },
          { value: "ambient", label: "轻微但持续的氛围诱导" },
          { value: "relationship_driven", label: "通过人物关系推动" },
          { value: "music_visual_driven", label: "通过音乐和画面氛围推动" },
        ],
      },
      {
        id: "negative_phase_preference",
        title: "Q21. 如果视频要进入负向阶段，您更能接受哪一种类型？",
        type: "single_select",
        required: true,
        options: [
          { value: "low_arousal_negative", label: "低唤醒负向：悲伤、失落、空旷" },
          { value: "medium_arousal_negative", label: "中等唤醒负向：压迫、焦虑、不确定" },
          { value: "high_arousal_negative", label: "高唤醒负向：恐惧、强紧张、惊吓" },
          { value: "avoid_negative", label: "尽量不进入负向阶段" },
        ],
      },
    ],
  },
];

export type SurveyAnswers = Record<string, unknown>;

export const questionIds = sections.flatMap((section) => section.questions.map((question) => question.id));
