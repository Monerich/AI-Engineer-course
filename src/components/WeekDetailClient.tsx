"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { curriculumData, WeekData } from "../data/curriculum";
import { 
  ArrowLeft, ArrowRight, CheckSquare, Square, 
  ExternalLink, CheckCircle, Award, HelpCircle, 
  BookOpen, ClipboardList, Play, ArrowLeftRight, Clock 
} from "lucide-react";

interface WeekDetailClientProps {
  lang: "ru" | "en";
  weekId: string;
  lectureHtml?: string;
  slidesHtml?: string;
  videoHtml?: string;
  slidesPdfUrl?: string;
  videoMp4Url?: string;
}

export default function WeekDetailClient({ 
  lang, 
  weekId,
  lectureHtml = "",
  slidesHtml = "",
  videoHtml = "",
  slidesPdfUrl,
  videoMp4Url
}: WeekDetailClientProps) {
  const router = useRouter();
  const content = curriculumData[lang];
  const common = content.common;
  const week = content.weeks[weekId] as WeekData;
  const weeks = Object.values(content.weeks).sort((a, b) => a.weekNum - b.weekNum);

  // States
  const [completedWeeks, setCompletedWeeks] = useState<string[]>(() => {
    if (typeof window === "undefined") return [];

    const savedWeeks = localStorage.getItem("ai_course_progress_weeks");
    if (!savedWeeks) return [];

    try {
      return JSON.parse(savedWeeks);
    } catch (e) {
      console.error(e);
      return [];
    }
  });
  const [checklistProgress, setChecklistProgress] = useState<Record<string, boolean>>(() => {
    if (typeof window === "undefined") return {};

    const savedChecklist = localStorage.getItem(`ai_course_checklist_${weekId}`);
    if (!savedChecklist) return {};

    try {
      return JSON.parse(savedChecklist);
    } catch (e) {
      console.error(e);
      return {};
    }
  });
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showQuizResults, setShowQuizResults] = useState(false);
  const [activeMaterialTab, setActiveMaterialTab] = useState<"lecture" | "slides" | "video">("lecture");

  if (!week) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-10 bg-[var(--bg-primary)]">
        <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-4">
          {lang === "ru" ? "Неделя не найдена" : "Week not found"}
        </h2>
        <Link href={`/${lang}`} className="text-[var(--accent)] font-semibold flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          {common.backToDashboard}
        </Link>
      </div>
    );
  }

  // Toggle checklist items
  const toggleChecklistItem = (itemIndex: number) => {
    const key = `item-${itemIndex}`;
    const newProgress = { ...checklistProgress, [key]: !checklistProgress[key] };
    setChecklistProgress(newProgress);
    localStorage.setItem(`ai_course_checklist_${weekId}`, JSON.stringify(newProgress));

    // Auto-mark week as complete if all checklist items are ticked
    const allTicked = week.checklist.every((_, i) => newProgress[`item-${i}`]);
    if (allTicked && !completedWeeks.includes(weekId)) {
      const updatedWeeks = [...completedWeeks, weekId];
      setCompletedWeeks(updatedWeeks);
      localStorage.setItem("ai_course_progress_weeks", JSON.stringify(updatedWeeks));
    }
  };

  // Toggle full week completion
  const toggleWeekCompletion = () => {
    let updatedWeeks = [...completedWeeks];
    if (completedWeeks.includes(weekId)) {
      updatedWeeks = updatedWeeks.filter((w) => w !== weekId);
    } else {
      updatedWeeks.push(weekId);
      // Auto-tick all checklist items
      const autoTicked: Record<string, boolean> = {};
      week.checklist.forEach((_, i) => {
        autoTicked[`item-${i}`] = true;
      });
      setChecklistProgress(autoTicked);
      localStorage.setItem(`ai_course_checklist_${weekId}`, JSON.stringify(autoTicked));
    }
    setCompletedWeeks(updatedWeeks);
    localStorage.setItem("ai_course_progress_weeks", JSON.stringify(updatedWeeks));
  };

  const handleSelectOption = (questionIndex: number, optionIndex: number) => {
    if (showQuizResults) return; // Lock choices after submission
    setSelectedAnswers({ ...selectedAnswers, [questionIndex]: optionIndex });
  };

  const submitQuiz = () => {
    setShowQuizResults(true);
  };

  // Navigation URLs
  const prevWeekNum = week.weekNum - 1;
  const nextWeekNum = week.weekNum + 1;
  const prevWeekUrl = prevWeekNum >= 1 ? `/${lang}/week-${prevWeekNum}` : null;
  const nextWeekUrl = nextWeekNum <= 26 ? `/${lang}/week-${nextWeekNum}` : null;

  return (
    <div className="flex-1 flex flex-col md:flex-row">
      
      {/* Sidebar - Timeline */}
      <aside className="w-full md:w-80 border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col max-h-screen sticky top-0 overflow-y-auto md:h-screen">
        <div className="p-6 border-b border-[var(--border)] flex flex-col gap-4">
          <Link
            href={`/${lang}`}
            className="text-xs font-semibold text-[var(--accent)] flex items-center gap-1.5 hover:text-[var(--accent-hover)]"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            {common.backToDashboard}
          </Link>
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-[var(--accent)]" />
            <h2 className="font-extrabold text-xs uppercase tracking-wider text-[var(--text-primary)]">
              {lang === "ru" ? "Содержание курса" : "Course Timeline"}
            </h2>
          </div>
        </div>

        <nav className="flex-1 p-4 flex flex-col gap-1.5">
          {weeks.map((w) => {
            const wId = `week-${w.weekNum}`;
            const isActive = weekId === wId;
            const isDone = completedWeeks.includes(wId);

            return (
              <Link
                key={w.weekNum}
                href={`/${lang}/${wId}`}
                className={`flex items-center justify-between p-3 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-[var(--sidebar-active)] border border-[var(--border)] text-[var(--text-primary)] font-black"
                    : "hover:bg-[var(--bg-primary)]/50 text-[var(--text-secondary)]"
                }`}
              >
                <div className="flex items-center gap-3 truncate">
                  <span className={`w-2 h-2 rounded-full flex-shrink-0 ${isDone ? "bg-green-500" : "bg-[var(--border)]"}`} />
                  <span className="truncate">
                    {common.weekHeader} {w.weekNum}: {w.title}
                  </span>
                </div>
                {isDone && <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0 ml-2" />}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-h-screen bg-[var(--bg-primary)]">
        <header className="sticky top-0 z-50 backdrop-blur-md bg-[var(--bg-primary)]/80 border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)] font-semibold uppercase tracking-wider">
            <span>{common.courseTitle}</span>
            <span>/</span>
            <span className="text-[var(--text-primary)] font-bold">
              {common.weekHeader} {week.weekNum}
            </span>
          </div>

          <button
            onClick={() => {
              const nextLang = lang === "ru" ? "en" : "ru";
              router.push(`/${nextLang}/${weekId}`);
            }}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[var(--border)] bg-[var(--bg-card)] hover:bg-[var(--bg-secondary)] text-xs font-semibold text-[var(--text-primary)] cursor-pointer"
          >
            <ArrowLeftRight className="w-3.5 h-3.5 text-[var(--accent)]" />
            {common.langSwitch}
          </button>
        </header>

        <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-10 flex flex-col gap-10">
          
          {/* Week Cover Header */}
          <section className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--accent)] uppercase tracking-wider bg-[var(--badge-bg)] px-2.5 py-1 rounded">
                {lang === "ru" ? `Месяц ${week.monthNum}` : `Month ${week.monthNum}`} • {common.weekHeader} {week.weekNum}
              </span>
              <span className="text-xs text-[var(--text-secondary)] font-bold flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-[var(--accent)]" />
                {week.duration} • {week.hours}
              </span>
            </div>

            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-[var(--text-primary)]">
              {week.title}
            </h1>
            <p className="text-sm md:text-base text-[var(--text-secondary)] leading-relaxed">
              {week.description}
            </p>
          </section>

          {/* Topics Card */}
          <section className="premium-card p-6 md:p-8">
            <h3 className="text-sm font-black uppercase tracking-wider text-[var(--text-primary)] mb-5 flex items-center gap-2.5 border-b border-[var(--border-light)] pb-3">
              <BookOpen className="w-5 h-5 text-[var(--accent)]" />
              {common.topicsTitle}
            </h3>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {week.topics.map((topic, i) => {
                const blockMatch = topic.match(/^(?:Блок|Block)\s+(\d+)/);
                const blockNum = blockMatch ? blockMatch[1] : null;
                return (
                  <li key={i} className="flex gap-2 text-xs font-semibold text-[var(--text-secondary)] leading-relaxed">
                    <span className="text-[var(--accent)] font-black">•</span>
                    {blockNum ? (
                      <button
                        className="text-left hover:text-[var(--accent)] transition-colors cursor-pointer"
                        onClick={() => {
                          setActiveMaterialTab("lecture");
                          setTimeout(() => {
                            const el = document.getElementById(`lecture-block-${blockNum}`);
                            if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
                          }, 50);
                        }}
                      >
                        {topic}
                      </button>
                    ) : (
                      <span>{topic}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>

          {/* Learning Materials Tabs */}
          {(lectureHtml || slidesPdfUrl || slidesHtml || videoMp4Url || videoHtml) && (
            <section className="premium-card p-6 md:p-8 flex flex-col gap-6">
              <div className="flex border-b border-[var(--border-light)] pb-2 gap-6 overflow-x-auto scrollbar-none">
                {lectureHtml && (
                  <button
                    onClick={() => setActiveMaterialTab("lecture")}
                    className={`pb-2.5 text-xs font-black uppercase tracking-wider transition-all cursor-pointer border-b-2 -mb-2.5 whitespace-nowrap ${
                      activeMaterialTab === "lecture"
                        ? "border-[var(--accent)] text-[var(--text-primary)]"
                        : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                  >
                    {lang === "ru" ? "📖 Урок / Лекция" : "📖 Lecture Lesson"}
                  </button>
                )}
                {(slidesPdfUrl || slidesHtml) && (
                  <button
                    onClick={() => setActiveMaterialTab("slides")}
                    className={`pb-2.5 text-xs font-black uppercase tracking-wider transition-all cursor-pointer border-b-2 -mb-2.5 whitespace-nowrap ${
                      activeMaterialTab === "slides"
                        ? "border-[var(--accent)] text-[var(--text-primary)]"
                        : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                  >
                    {lang === "ru" ? "📊 Презентация" : "📊 Presentation"}
                  </button>
                )}
                {(videoMp4Url || videoHtml) && (
                  <button
                    onClick={() => setActiveMaterialTab("video")}
                    className={`pb-2.5 text-xs font-black uppercase tracking-wider transition-all cursor-pointer border-b-2 -mb-2.5 whitespace-nowrap ${
                      activeMaterialTab === "video"
                        ? "border-[var(--accent)] text-[var(--text-primary)]"
                        : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                  >
                    {lang === "ru" ? "🎥 Видеоурок" : "🎥 Video Lesson"}
                  </button>
                )}
              </div>

              {/* Tab Content Rendering */}
              <div className="prose dark:prose-invert max-w-none text-xs font-semibold leading-relaxed text-[var(--text-primary)]">
                {activeMaterialTab === "lecture" && lectureHtml && (
                  <div 
                    className="flex flex-col gap-4 markdown-content"
                    dangerouslySetInnerHTML={{ __html: lectureHtml }}
                  />
                )}
                
                {activeMaterialTab === "slides" && (
                  slidesPdfUrl ? (
                    <div className="w-full h-[450px] md:h-[600px] border border-[var(--border)] rounded-2xl overflow-hidden shadow-lg bg-[var(--bg-secondary)]">
                      <iframe
                        src={`${slidesPdfUrl}#view=FitH`}
                        className="w-full h-full border-0"
                        title="NotebookLM Slide Deck"
                      />
                    </div>
                  ) : (
                    slidesHtml && (
                      <div 
                        className="flex flex-col gap-4 markdown-content slides-layout"
                        dangerouslySetInnerHTML={{ __html: slidesHtml }}
                      />
                    )
                  )
                )}
                
                {activeMaterialTab === "video" && (
                  videoMp4Url ? (
                    <div className="relative w-full aspect-video border border-[var(--border)] rounded-2xl overflow-hidden shadow-xl bg-black flex items-center justify-center">
                      <video
                        src={videoMp4Url}
                        controls
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    videoHtml && (
                      <div 
                        className="flex flex-col gap-4 markdown-content video-script-layout"
                        dangerouslySetInnerHTML={{ __html: videoHtml }}
                      />
                    )
                  )
                )}
              </div>
            </section>
          )}

          {/* Resources Card */}
          {week.resources && week.resources.length > 0 && (
            <section className="premium-card p-6 md:p-8">
              <h3 className="text-sm font-black uppercase tracking-wider text-[var(--text-primary)] mb-5 flex items-center gap-2.5 border-b border-[var(--border-light)] pb-3">
                <ExternalLink className="w-5 h-5 text-[var(--accent)]" />
                {common.resourcesTitle}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {week.resources.map((res, i) => (
                  <a
                    key={i}
                    href={res.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-4 rounded-lg border border-[var(--border-light)] hover:border-[var(--accent)] bg-[var(--bg-secondary)]/30 hover:bg-[var(--bg-secondary)]"
                  >
                    <span className="text-xs font-bold text-[var(--text-primary)] truncate pr-4">
                      {res.name}
                    </span>
                    <ExternalLink className="w-4 h-4 text-[var(--accent)] flex-shrink-0" />
                  </a>
                ))}
              </div>
            </section>
          )}

          {/* Readiness Checklist */}
          <section className="premium-card p-6 md:p-8">
            <h3 className="text-sm font-black uppercase tracking-wider text-[var(--text-primary)] mb-5 flex items-center gap-2.5 border-b border-[var(--border-light)] pb-3">
              <ClipboardList className="w-5 h-5 text-[var(--accent)]" />
              {common.checklistTitle}
            </h3>
            <div className="flex flex-col gap-1">
              {week.checklist.map((item, i) => {
                const isChecked = checklistProgress[`item-${i}`] || false;
                return (
                  <div
                    key={i}
                    onClick={() => toggleChecklistItem(i)}
                    className="checklist-item"
                  >
                    {isChecked ? (
                      <CheckSquare className="w-4.5 h-4.5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <Square className="w-4.5 h-4.5 text-[var(--border)] flex-shrink-0 mt-0.5" />
                    )}
                    <span className={`text-xs font-semibold leading-relaxed ${isChecked ? "line-through text-[var(--text-secondary)]" : "text-[var(--text-primary)]"}`}>
                      {item}
                    </span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Homework Card */}
          <section className="premium-card p-6 md:p-8">
            <h3 className="text-sm font-black uppercase tracking-wider text-[var(--text-primary)] mb-5 flex items-center gap-2.5 border-b border-[var(--border-light)] pb-3">
              <Play className="w-5 h-5 text-[var(--accent)]" />
              {common.homeworkTitle}: {week.homework.title}
            </h3>
            <p className="text-xs font-semibold text-[var(--text-secondary)] mb-6 leading-relaxed">
              {week.homework.description}
            </p>
            <div className="flex flex-col gap-4">
              {week.homework.steps.map((step, i) => (
                <div key={i} className="flex gap-4">
                  <div className="w-6 h-6 rounded-full bg-[var(--badge-bg)] text-[10px] font-black text-[var(--accent)] flex items-center justify-center flex-shrink-0 mt-0.5">
                    {i + 1}
                  </div>
                  <p className="text-xs font-semibold text-[var(--text-secondary)] leading-relaxed">
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Quiz Card */}
          {week.quiz && week.quiz.length > 0 && (
            <section className="premium-card p-6 md:p-8">
              <h3 className="text-sm font-black uppercase tracking-wider text-[var(--text-primary)] mb-5 flex items-center gap-2.5 border-b border-[var(--border-light)] pb-3">
                <HelpCircle className="w-5 h-5 text-[var(--accent)]" />
                {common.quizTitle}
              </h3>
              
              <div className="flex flex-col gap-8">
                {week.quiz.map((q, qIdx) => {
                  const selectedOpt = selectedAnswers[qIdx];
                  const isCorrect = selectedOpt === q.answerIndex;
                  
                  return (
                    <div key={qIdx} className="flex flex-col gap-4">
                      <h4 className="text-xs font-bold text-[var(--text-primary)] leading-relaxed">
                        {qIdx + 1}. {q.question}
                      </h4>
                      
                      <div className="flex flex-col gap-2">
                        {q.options.map((opt, oIdx) => {
                          const isOptionSelected = selectedOpt === oIdx;
                          let optionClass = "border-[var(--border)] bg-[var(--bg-card)] hover:bg-[var(--bg-secondary)] text-[var(--text-primary)]";
                          
                          if (showQuizResults) {
                            if (oIdx === q.answerIndex) {
                              // Highlight correct answer
                              optionClass = "border-green-500 bg-green-500/10 text-green-700 dark:text-green-300";
                            } else if (isOptionSelected) {
                              // Highlight incorrect selection
                              optionClass = "border-red-500 bg-red-500/10 text-red-700 dark:text-red-300";
                            } else {
                              optionClass = "border-[var(--border)] bg-[var(--bg-card)] opacity-60 text-[var(--text-secondary)]";
                            }
                          } else if (isOptionSelected) {
                            optionClass = "border-[var(--accent)] bg-[var(--accent)]/5 text-[var(--text-primary)] font-black";
                          }

                          return (
                            <button
                              key={oIdx}
                              onClick={() => handleSelectOption(qIdx, oIdx)}
                              className={`text-left p-3.5 rounded-lg border text-xs font-semibold leading-relaxed transition-all cursor-pointer ${optionClass}`}
                              disabled={showQuizResults}
                            >
                              {opt}
                            </button>
                          );
                        })}
                      </div>

                      {showQuizResults && (
                        <div className={`p-4 rounded-lg text-xs leading-relaxed border ${
                          isCorrect 
                            ? "bg-green-500/5 border-green-500/20 text-green-700 dark:text-green-300"
                            : "bg-red-500/5 border-red-500/20 text-red-700 dark:text-red-300"
                        }`}>
                          <p className="font-bold mb-1">
                            {isCorrect ? `✓ ${common.correct}` : `✗ ${common.incorrect}`}
                          </p>
                          <p>{q.explanation}</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {!showQuizResults ? (
                <button
                  onClick={submitQuiz}
                  disabled={Object.keys(selectedAnswers).length < week.quiz.length}
                  className="mt-8 w-full py-3 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] disabled:bg-[var(--border)] text-xs font-bold text-white transition-colors cursor-pointer"
                >
                  {common.submitQuiz}
                </button>
              ) : (
                <div className="mt-8 text-center text-xs font-bold">
                  {Object.values(selectedAnswers).every((ans, i) => ans === week.quiz[i].answerIndex) ? (
                    <p className="text-green-600 dark:text-green-400">{common.quizPassed}</p>
                  ) : (
                    <p className="text-red-500">{common.quizFailed}</p>
                  )}
                </div>
              )}
            </section>
          )}

          {/* Dynamic Action Buttons */}
          <section className="flex flex-col sm:flex-row items-center gap-4 justify-between mt-6 pt-6 border-t border-[var(--border)]">
            <button
              onClick={toggleWeekCompletion}
              className={`w-full sm:w-auto px-6 py-3 rounded-lg text-xs font-bold flex items-center justify-center gap-2 border transition-all cursor-pointer ${
                completedWeeks.includes(weekId)
                  ? "bg-green-600 border-green-600 text-white hover:bg-green-700 shadow-sm"
                  : "bg-[var(--bg-card)] border-[var(--border)] text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] shadow-sm"
              }`}
            >
              <CheckCircle className="w-4 h-4" />
              {completedWeeks.includes(weekId)
                ? (lang === "ru" ? "Снять отметку о прохождении" : "Mark as Incomplete")
                : (lang === "ru" ? "Отметить неделю как пройденную" : "Mark as Completed")}
            </button>

            <div className="flex items-center gap-4 w-full sm:w-auto justify-end">
              {prevWeekUrl ? (
                <Link
                  href={prevWeekUrl}
                  className="px-4 py-2 rounded-lg border border-[var(--border)] text-xs font-bold text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] flex items-center gap-1.5 shadow-sm"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  {common.prevWeek}
                </Link>
              ) : (
                <span className="opacity-0 px-4 py-2" />
              )}

              {nextWeekUrl ? (
                <Link
                  href={nextWeekUrl}
                  className="px-4 py-2 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] text-xs font-bold text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] flex items-center gap-1.5 shadow-sm"
                >
                  {common.nextWeek}
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              ) : (
                <span className="opacity-0 px-4 py-2" />
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
