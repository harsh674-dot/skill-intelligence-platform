"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type Language = "en" | "hi";

export interface Translations {
  // Navigation & General
  brandTitle: string;
  brandSubtitle: string;
  sihBadge: string;
  apiOnline: string;
  apiOffline: string;
  tabEmployee: string;
  tabAssessments: string;
  tabRagStudio: string;
  tabAdmin: string;
  selectPersona: string;
  judgeSwitcherTitle: string;
  judgeSwitcherSub: string;
  languageSelect: string;
  englishLabel: string;
  hindiLabel: string;

  // Roles & Departments
  roleStatisticalOfficer: string;
  roleDataAnalyst: string;
  roleSeniorStatisticalOfficer: string;
  roleSystemAdmin: string;
  deptNSO: string;
  deptNSSO: string;
  deptStateDirectorate: string;

  // Employee Dashboard
  welcomeBack: string;
  assignedRole: string;
  welcomeDesc: string;
  takeAssessment: string;
  requiredSkills: string;
  requiredSkillsDesc: string;
  activeGaps: string;
  activeGapsDesc: string;
  masteredSkills: string;
  masteredSkillsDesc: string;
  learningCourses: string;
  learningCoursesDesc: string;
  topographyTitle: string;
  topographyDesc: string;
  skillGapEngineTitle: string;
  skillGapEngineFormula: string;
  actionableGaps: string;
  priorityScore: string;
  currentLevel: string;
  targetLevel: string;
  levelGap: string;
  critical: string;
  mastered: string;
  noGapsDetected: string;
  learningPathwaysTitle: string;
  learningPathwaysSubtitle: string;
  launchQuiz: string;
  durationMins: string;
  targets: string;
  noRecommendations: string;
  benchmarkMatrixTitle: string;
  benchmarkMatrixDesc: string;
  allDomains: string;

  // 3D Skill Topography Legends
  statDomain: string;
  techDomain: string;
  domainDomain: string;
  softDomain: string;

  // Assessment Arena
  assessmentArenaTitle: string;
  assessmentArenaDesc: string;
  launchAssessment: string;
  targetedCompetencies: string;
  assemblingQuestions: string;
  questionOf: string;
  difficulty: string;
  correctAnswer: string;
  incorrectAnswer: string;
  nextQuestion: string;
  submitAndUpgrade: string;
  calculatingNext: string;
  competencyLoopClosed: string;
  ruleAppliedDesc: string;
  totalScore: string;
  correct: string;
  upgrades: string;
  progressionDeltas: string;
  evidenceLevel: string;
  updateDashboardBtn: string;

  // Workforce Analytics
  workforceDashboardTitle: string;
  workforceDashboardSubtitle: string;
  officersSynced: string;
  totalHeadcount: string;
  totalHeadcountDesc: string;
  systemicGaps: string;
  systemicGapsDesc: string;
  upgradesViaLoop: string;
  avgScore: string;
  aiQuestionPool: string;
  approvedInCirculation: string;
  topDeficitsTitle: string;
  topDeficitsSubtitle: string;
  officersImpacted: string;
  totalPriority: string;
  totalGapLevels: string;
  proficiencyDistributionTitle: string;
  proficiencyDistributionDesc: string;
  intermediatePlus: string;
  gapsRemaining: string;
  domainHealthTitle: string;
  basedOnEvaluations: string;

  // Admin Studio
  aiStudioTitle: string;
  aiStudioSubtitle: string;
  subtabIngestion: string;
  subtabGenerate: string;
  subtabReviewQueue: string;
  uploadCourseMaterial: string;
  uploadDesc: string;
  dragOrClickUpload: string;
  uploadingStatus: string;
  ingestedLibrary: string;
  chunksCount: string;
  ragInspectorTitle: string;
  selectDocToInspect: string;
  viewingChunks: string;
  chunkLabel: string;
  vectorEmbedded: string;
  clickDocLeft: string;
  aiGeneratorTitle: string;
  aiGeneratorSubtitle: string;
  targetMaterialLabel: string;
  difficultyLevelLabel: string;
  questionCountLabel: string;
  diffBeginner: string;
  diffIntermediate: string;
  diffAdvanced: string;
  btnGenerateRAG: string;
  generatingStatus: string;
  filterStatusLabel: string;
  filterAll: string;
  filterPending: string;
  filterApproved: string;
  filterRejected: string;
  showingQuestions: string;
  btnEditQuestion: string;
  btnReject: string;
  btnApprove: string;
  explanationLabel: string;

  // Tour Guide & Extra UI
  tourGuideTitle: string;
  tourGuideStep: string;
  stepNext: string;
  tourGuideCollapsed: string;
  tourGuideStepOf: string;
  loadingMatrix: string;
  noActiveRole: string;
  loadAnanya: string;
  retryBtn: string;
}

const TRANSLATIONS: Record<Language, Translations> = {
  en: {
    brandTitle: "Skill Intelligence",
    brandSubtitle: "MoSPI Capacity Building & Competency Engine",
    sihBadge: "SIH26101",
    apiOnline: "API Online",
    apiOffline: "Offline",
    tabEmployee: "Employee Dashboard",
    tabAssessments: "Assessment Arena",
    tabRagStudio: "RAG & AI Studio",
    tabAdmin: "Workforce Analytics",
    selectPersona: "Select Persona",
    judgeSwitcherTitle: "Judge / Persona Switcher",
    judgeSwitcherSub: "Select a role to test different workflows:",
    languageSelect: "Language",
    englishLabel: "English",
    hindiLabel: "हिंदी",

    roleStatisticalOfficer: "Statistical Officer",
    roleDataAnalyst: "Data Analyst",
    roleSeniorStatisticalOfficer: "Senior Statistical Officer",
    roleSystemAdmin: "System Admin",
    deptNSO: "National Statistical Office",
    deptNSSO: "National Sample Survey Office",
    deptStateDirectorate: "State Directorate of Economics",

    welcomeBack: "Welcome back,",
    assignedRole: "Assigned Job Role:",
    welcomeDesc: "Review your required vs. current competency benchmarks, prioritize skill gaps, and explore tailored learning pathways.",
    takeAssessment: "Take Assessment",
    requiredSkills: "Required Skills",
    requiredSkillsDesc: "Role requirement benchmark",
    activeGaps: "Active Gaps",
    activeGapsDesc: "Ranked by priority formula",
    masteredSkills: "Mastered Skills",
    masteredSkillsDesc: "Meeting or exceeding requirement",
    learningCourses: "Learning Courses",
    learningCoursesDesc: "Matched to high-priority gaps",
    topographyTitle: "3D Competency Topography",
    topographyDesc: "Interactive 3D representation of competency nodes and domain linkages",
    skillGapEngineTitle: "Skill-Gap & Priority Engine",
    skillGapEngineFormula: "Priority = (Gap × 2) + (Criticality × 3) + TargetLevel",
    actionableGaps: "Actionable Gaps",
    priorityScore: "Priority Score:",
    currentLevel: "Current:",
    targetLevel: "Target:",
    levelGap: "Level Gap",
    critical: "Critical",
    mastered: "Mastered",
    noGapsDetected: "🎉 No competency gaps detected! You meet or exceed all role requirements.",
    learningPathwaysTitle: "Personalized Learning Pathways",
    learningPathwaysSubtitle: "Integrated iGOT Karmayogi & TPAC Courses",
    launchQuiz: "Launch Quiz",
    durationMins: "mins",
    targets: "Targets:",
    noRecommendations: "No pending recommendations. Take an assessment to discover targeted courses.",
    benchmarkMatrixTitle: "Role Competency Benchmark Matrix",
    benchmarkMatrixDesc: "Evaluated on standard 1–5 scale (Beginner, Basic, Intermediate, Advanced, Expert)",
    allDomains: "All",

    statDomain: "Statistical",
    techDomain: "Technical",
    domainDomain: "Domain",
    softDomain: "Soft Skills",

    assessmentArenaTitle: "Adaptive Assessment Arena",
    assessmentArenaDesc: "Take an adaptive competency assessment to test statistical and technical competencies. Submitting answers executes the 40% previous + 60% evidence combination rule, updating your skill profile and refreshing personalized course recommendations.",
    launchAssessment: "Launch Competency Assessment",
    targetedCompetencies: "Competencies Targeted in Next Assessment:",
    assemblingQuestions: "Assembling competency questions...",
    questionOf: "Question",
    difficulty: "Difficulty:",
    correctAnswer: "Correct Answer",
    incorrectAnswer: "Incorrect",
    nextQuestion: "Next Question",
    submitAndUpgrade: "Submit & Upgrade Competencies",
    calculatingNext: "Calculating Next...",
    competencyLoopClosed: "Competency Progression Updated",
    ruleAppliedDesc: "Applied combination rule: 40% previous competency + 60% new evidence.",
    totalScore: "Total Score",
    correct: "Correct",
    upgrades: "Upgrades",
    progressionDeltas: "Competency Progression Deltas",
    evidenceLevel: "Evidence Level:",
    updateDashboardBtn: "Update Dashboard & View Gaps",

    workforceDashboardTitle: "Organizational Competency Dashboard",
    workforceDashboardSubtitle: "Macro-level telemetry across India's Official Statistical System. Identify critical capacity bottlenecks, measure training effectiveness, and track competency shifts across departments.",
    officersSynced: "Officers Synced",
    totalHeadcount: "Total Headcount",
    totalHeadcountDesc: "Across Statistical Divisions",
    systemicGaps: "Systemic Gaps",
    systemicGapsDesc: "Tagged Mission-Critical",
    upgradesViaLoop: "Upgrades via Loop",
    avgScore: "Average Quiz Score:",
    aiQuestionPool: "AI Question Pool",
    approvedInCirculation: "Approved & In Circulation",
    topDeficitsTitle: "Top Priority Skill Deficits",
    topDeficitsSubtitle: "Aggregated by cumulative gap size and organizational priority",
    officersImpacted: "Officers Impacted",
    totalPriority: "Priority",
    totalGapLevels: "Total Gap: -",
    proficiencyDistributionTitle: "Workforce Proficiency Distribution",
    proficiencyDistributionDesc: "Total competency evaluations across standard proficiency tiers",
    intermediatePlus: "Intermediate+",
    gapsRemaining: "Gaps Remaining",
    domainHealthTitle: "Domain Competency Health Index",
    basedOnEvaluations: "Based on evaluations",

    aiStudioTitle: "AI Learning & Question Studio",
    aiStudioSubtitle: "Upload approved statistical courseware (PDF/DOCX/TXT), inspect chunks and vector embeddings, generate grounded MCQs via LLM, and review questions before publishing to the live assessment bank.",
    subtabIngestion: "Ingestion & Chunks",
    subtabGenerate: "Generate MCQs",
    subtabReviewQueue: "Review Queue",
    uploadCourseMaterial: "Upload Course Material",
    uploadDesc: "Supported formats: PDF, DOCX, TXT. Documents are extracted, chunked, and embedded into pgvector.",
    dragOrClickUpload: "Click or Drag to Upload",
    uploadingStatus: "Extracting & Embedding Chunks...",
    ingestedLibrary: "Ingested Content Library",
    chunksCount: "Chunks",
    ragInspectorTitle: "RAG Chunk & Vector Inspector",
    selectDocToInspect: "Select a document to inspect chunks",
    viewingChunks: "Viewing extracted chunks",
    chunkLabel: "Chunk #",
    vectorEmbedded: "384D Vector Embedded",
    clickDocLeft: "Click any document on the left to inspect its segmented vector chunks.",
    aiGeneratorTitle: "AI Grounded Quiz Generator",
    aiGeneratorSubtitle: "Retrieves semantic chunks from the selected document and prompts the model to generate strict, grounded MCQs with verified correct answers.",
    targetMaterialLabel: "Target Learning Material",
    difficultyLevelLabel: "Difficulty Level",
    questionCountLabel: "Question Count",
    diffBeginner: "Beginner (Concepts)",
    diffIntermediate: "Intermediate (Application)",
    diffAdvanced: "Advanced (Deep Analysis)",
    btnGenerateRAG: "Synthesize Questions via RAG",
    generatingStatus: "Generating Grounded MCQs...",
    filterStatusLabel: "Filter Status:",
    filterAll: "All",
    filterPending: "Pending",
    filterApproved: "Approved",
    filterRejected: "Rejected",
    showingQuestions: "Showing Questions",
    btnEditQuestion: "Edit Question",
    btnReject: "Reject",
    btnApprove: "Approve & Publish",
    explanationLabel: "Explanation:",

    tourGuideTitle: "Judge Tour Guide",
    tourGuideStep: "Step",
    stepNext: "Next Step",
    tourGuideCollapsed: "Judge Tour Guide",
    tourGuideStepOf: "Step",
    loadingMatrix: "Loading competency matrix & priority gaps...",
    noActiveRole: "User does not have an active job role assigned. Switch to a demo persona like Ananya Sharma.",
    loadAnanya: "Load Ananya Sharma (Statistical Officer)",
    retryBtn: "Retry",
  },
  hi: {
    brandTitle: "कौशल बुद्धिमत्ता",
    brandSubtitle: "सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय • क्षमता निर्माण एवं योग्यता इंजन",
    sihBadge: "एस.आई.एच.26101",
    apiOnline: "एपीआई ऑनलाइन",
    apiOffline: "ऑफ़लाइन",
    tabEmployee: "कर्मचारी डैशबोर्ड",
    tabAssessments: "मूल्यांकन अखाड़ा",
    tabRagStudio: "आरएजी और एआई स्टूडियो",
    tabAdmin: "कार्यबल विश्लेषण",
    selectPersona: "पात्र चुनें",
    judgeSwitcherTitle: "निर्णायक / पात्र स्विचर",
    judgeSwitcherSub: "विभिन्न कार्यप्रवाहों का परीक्षण करने के लिए एक भूमिका चुनें:",
    languageSelect: "भाषा (Language)",
    englishLabel: "English",
    hindiLabel: "हिंदी",

    roleStatisticalOfficer: "सांख्यिकी अधिकारी",
    roleDataAnalyst: "डेटा विश्लेषक",
    roleSeniorStatisticalOfficer: "वरिष्ठ सांख्यिकी अधिकारी",
    roleSystemAdmin: "सिस्टम प्रशासक",
    deptNSO: "राष्ट्रीय सांख्यिकी कार्यालय (NSO)",
    deptNSSO: "राष्ट्रीय प्रतिदर्श सर्वेक्षण कार्यालय (NSSO)",
    deptStateDirectorate: "राज्य अर्थशास्त्र निदेशालय",

    welcomeBack: "पुनः स्वागत है,",
    assignedRole: "निर्धारित पद भूमिका:",
    welcomeDesc: "अपनी आवश्यक बनाम वर्तमान दक्षताओं की समीक्षा करें, कौशल अंतरालों को प्राथमिकता दें और अनुरूप शिक्षण मार्गों का अन्वेषण करें।",
    takeAssessment: "मूल्यांकन लें",
    requiredSkills: "आवश्यक कौशल",
    requiredSkillsDesc: "भूमिका आवश्यकता मानदंड",
    activeGaps: "सक्रिय अंतराल",
    activeGapsDesc: "प्राथमिकता सूत्र अनुसार श्रेणीबद्ध",
    masteredSkills: "दक्ष कौशल",
    masteredSkillsDesc: "आवश्यकता के समकक्ष या अधिक",
    learningCourses: "अधिगम पाठ्यक्रम",
    learningCoursesDesc: "उच्च प्राथमिकता अंतरालों से मेल खाते",
    topographyTitle: "3D योग्यता स्थलाकृति",
    topographyDesc: "योग्यता नोड्स और डोमेन संपर्कों का संवादात्मक 3D चित्रण",
    skillGapEngineTitle: "कौशल-अंतराल एवं प्राथमिकता इंजन",
    skillGapEngineFormula: "प्राथमिकता = (अंतराल × 2) + (महत्व × 3) + लक्षित स्तर",
    actionableGaps: "कार्रवाई योग्य अंतराल",
    priorityScore: "प्राथमिकता स्कोर:",
    currentLevel: "वर्तमान:",
    targetLevel: "लक्षित:",
    levelGap: "स्तर अंतराल",
    critical: "अति महत्वपूर्ण",
    mastered: "दक्ष",
    noGapsDetected: "🎉 कोई कौशल अंतराल नहीं पाया गया! आप अपनी सभी भूमिका आवश्यकताओं में दक्ष हैं।",
    learningPathwaysTitle: "व्यक्तिगत शिक्षण मार्ग",
    learningPathwaysSubtitle: "एकीकृत iGOT कर्मयोगी एवं TPAC पाठ्यक्रम",
    launchQuiz: "क्विज़ प्रारंभ करें",
    durationMins: "मिनट",
    targets: "लक्षित कौशल:",
    noRecommendations: "कोई लंबित सिफारिश नहीं है। अनुरूप पाठ्यक्रम खोजने के लिए मूल्यांकन लें।",
    benchmarkMatrixTitle: "भूमिका योग्यता मानदंड मैट्रिक्स",
    benchmarkMatrixDesc: "मानक 1–5 पैमाने पर मूल्यांकित (प्रारंभिक, बुनियादी, मध्यम, उन्नत, विशेषज्ञ)",
    allDomains: "सभी",

    statDomain: "सांख्यिकी",
    techDomain: "तकनीकी",
    domainDomain: "डोमेन",
    softDomain: "सॉफ्ट स्किल्स",

    assessmentArenaTitle: "अनुकूली मूल्यांकन अखाड़ा",
    assessmentArenaDesc: "सांख्यिकीय और तकनीकी दक्षताओं का परीक्षण करने हेतु अनुकूली मूल्यांकन लें। उत्तर जमा करने पर 40% पिछला स्तर + 60% नया साक्ष्य संयोजन नियम लागू होता है, जिससे आपका कौशल प्रोफाइल तुरंत अपडेट होता है।",
    launchAssessment: "योग्यता मूल्यांकन प्रारंभ करें",
    targetedCompetencies: "आगामी मूल्यांकन में लक्षित दक्षताएं:",
    assemblingQuestions: "योग्यता प्रश्न संकलित किए जा रहे हैं...",
    questionOf: "प्रश्न",
    difficulty: "कठिनाई:",
    correctAnswer: "सही उत्तर",
    incorrectAnswer: "गलत उत्तर",
    nextQuestion: "अगला प्रश्न",
    submitAndUpgrade: "जमा करें और दक्षता अपग्रेड करें",
    calculatingNext: "अगला प्रश्न लोड हो रहा है...",
    competencyLoopClosed: "दक्षता प्रगति अद्यतन हुई",
    ruleAppliedDesc: "लागू संयोजन नियम: 40% पिछली दक्षता + 60% नया साक्ष्य।",
    totalScore: "कुल प्राप्तांक",
    correct: "सही",
    upgrades: "अपग्रेड",
    progressionDeltas: "योग्यता प्रगति अंतर",
    evidenceLevel: "साक्ष्य स्तर:",
    updateDashboardBtn: "डैशबोर्ड अपडेट करें और अंतराल देखें",

    workforceDashboardTitle: "संगठनात्मक योग्यता डैशबोर्ड",
    workforceDashboardSubtitle: "भारत की आधिकारिक सांख्यिकीय प्रणाली का व्यापक विश्लेषण। महत्वपूर्ण क्षमता बाधाओं की पहचान करें, प्रशिक्षण प्रभावशीलता मापें और विभागों में दक्षता प्रगति ट्रैक करें।",
    officersSynced: "अधिकारी समन्वयित",
    totalHeadcount: "कुल कर्मचारी संख्या",
    totalHeadcountDesc: "सांख्यिकीय प्रभागों में",
    systemicGaps: "प्रणालीगत अंतराल",
    systemicGapsDesc: "मिशन-क्रिटिकल चिह्नित",
    upgradesViaLoop: "लूप द्वारा अपग्रेड",
    avgScore: "औसत क्विज़ स्कोर:",
    aiQuestionPool: "एआई प्रश्न बैंक",
    approvedInCirculation: "स्वीकृत और उपयोग में",
    topDeficitsTitle: "शीर्ष प्राथमिकता कौशल अंतराल",
    topDeficitsSubtitle: "कुल अंतराल आकार और संगठनात्मक प्राथमिकता के आधार पर संकलित",
    officersImpacted: "प्रभावित अधिकारी",
    totalPriority: "प्राथमिकता",
    totalGapLevels: "कुल अंतराल: -",
    proficiencyDistributionTitle: "कार्यबल दक्षता वितरण",
    proficiencyDistributionDesc: "मानक दक्षता स्तरों के तहत कुल योग्यता मूल्यांकन",
    intermediatePlus: "मध्यम या अधिक",
    gapsRemaining: "शेष अंतराल",
    domainHealthTitle: "डोमेन योग्यता स्वास्थ्य सूचकांक",
    basedOnEvaluations: "मूल्यांकनों पर आधारित",

    aiStudioTitle: "एआई शिक्षण एवं प्रश्न स्टूडियो",
    aiStudioSubtitle: "स्वीकृत सांख्यिकीय पाठ्यक्रम सामग्री (PDF/DOCX/TXT) अपलोड करें, वेक्टर चंक्स का निरीक्षण करें, एलएलएम द्वारा आधारित प्रश्न उत्पन्न करें और बैंक में प्रकाशित करने से पहले समीक्षा करें।",
    subtabIngestion: "प्रविष्टि एवं भाग",
    subtabGenerate: "एमसीक्यू तैयार करें",
    subtabReviewQueue: "समीक्षा कतार",
    uploadCourseMaterial: "पाठ्यक्रम सामग्री अपलोड करें",
    uploadDesc: "समर्थित प्रारूप: PDF, DOCX, TXT। दस्तावेज़ निकाल कर pgvector में 384D वेक्टर के रूप में सन्निहित किए जाते हैं।",
    dragOrClickUpload: "अपलोड करने के लिए क्लिक करें या फ़ाइल खींचें",
    uploadingStatus: "सामग्री विश्लेषण एवं वेक्टर एम्बेडिंग प्रगति पर...",
    ingestedLibrary: "प्रविष्ट सामग्री पुस्तकालय",
    chunksCount: "भाग",
    ragInspectorTitle: "आरएजी भाग एवं वेक्टर निरीक्षक",
    selectDocToInspect: "भागों के निरीक्षण हेतु दस्तावेज़ चुनें",
    viewingChunks: "निकाले गए भागों का अवलोकन",
    chunkLabel: "भाग #",
    vectorEmbedded: "384D वेक्टर सन्निहित",
    clickDocLeft: "दस्तावेज़ के विभाजित वेक्टर भागों को देखने के लिए बाईं ओर किसी भी फ़ाइल पर क्लिक करें।",
    aiGeneratorTitle: "एआई आधारित क्विज़ जनरेटर",
    aiGeneratorSubtitle: "चयनित दस्तावेज़ से प्रासंगिक अंश निकालता है और सत्यापित सही उत्तरों के साथ आधारित प्रश्न तैयार करता है।",
    targetMaterialLabel: "लक्षित शिक्षण सामग्री",
    difficultyLevelLabel: "कठिनाई स्तर",
    questionCountLabel: "प्रश्नों की संख्या",
    diffBeginner: "प्रारंभिक (सिद्धांत)",
    diffIntermediate: "मध्यम (अनुप्रयोग)",
    diffAdvanced: "उन्नत (गहन विश्लेषण)",
    btnGenerateRAG: "आरएजी द्वारा प्रश्न तैयार करें",
    generatingStatus: "आधारित प्रश्न उत्पन्न किए जा रहे हैं...",
    filterStatusLabel: "स्थिति फ़िल्टर:",
    filterAll: "सभी",
    filterPending: "लंबित",
    filterApproved: "स्वीकृत",
    filterRejected: "अस्वीकृत",
    showingQuestions: "प्रदर्शित प्रश्न",
    btnEditQuestion: "प्रश्न संपादित करें",
    btnReject: "अस्वीकार करें",
    btnApprove: "स्वीकार करें एवं प्रकाशित करें",
    explanationLabel: "स्पष्टीकरण:",

    tourGuideTitle: "निर्णायक टूर गाइड",
    tourGuideStep: "चरण",
    stepNext: "अगला चरण",
    tourGuideCollapsed: "निर्णायक टूर गाइड",
    tourGuideStepOf: "चरण",
    loadingMatrix: "दक्षता मैट्रिक्स और प्राथमिकता अंतराल लोड हो रहे हैं...",
    noActiveRole: "उपयोगकर्ता को कोई सक्रिय पद भूमिका निर्धारित नहीं है। अनन्या शर्मा जैसे डेमो पात्र पर स्विच करें।",
    loadAnanya: "अनन्या शर्मा (सांख्यिकी अधिकारी) लोड करें",
    retryBtn: "पुनः प्रयास करें",
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    const saved = localStorage.getItem("app_language") as Language | null;
    if (saved === "en" || saved === "hi") {
      setLanguageState(saved);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("app_language", lang);
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t: TRANSLATIONS[language],
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
