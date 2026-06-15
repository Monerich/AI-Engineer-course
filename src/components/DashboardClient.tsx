"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { curriculumData } from "../data/curriculum";
import { Globe, Award, CheckCircle, ChevronRight } from "lucide-react";

interface DashboardClientProps {
  lang: "ru" | "en";
}

export default function DashboardClient({ lang }: DashboardClientProps) {
  const router = useRouter();
  const content = curriculumData[lang];
  const common = content.common;
  const weeks = Object.values(content.weeks).sort((a, b) => a.weekNum - b.weekNum);

  // Client-side progress state
  const [completedWeeks] = useState<string[]>(() => {
    if (typeof window === "undefined") return [];

    const saved = localStorage.getItem("ai_course_progress_weeks");
    if (!saved) return [];

    try {
      return JSON.parse(saved);
    } catch (e) {
      console.error(e);
      return [];
    }
  });
  const [activeMonth, setActiveMonth] = useState<number | null>(null);

  const totalWeeksCount = weeks.length;
  const completedCount = completedWeeks.length;
  const percentComplete = totalWeeksCount > 0 ? Math.round((completedCount / totalWeeksCount) * 100) : 0;

  const toggleLanguage = () => {
    const nextLang = lang === "ru" ? "en" : "ru";
    router.push(`/${nextLang}`);
  };

  const getMonthName = (monthNum: number) => {
    if (lang === "ru") {
      return `Месяц ${monthNum}`;
    }
    return `Month ${monthNum}`;
  };

  // Group weeks by month
  const weeksByMonth: Record<number, typeof weeks> = {};
  weeks.forEach((w) => {
    if (!weeksByMonth[w.monthNum]) {
      weeksByMonth[w.monthNum] = [];
    }
    weeksByMonth[w.monthNum].push(w);
  });

  const months = Object.keys(weeksByMonth).map(Number).sort((a, b) => a - b);

  return (
    <div className="flex-1 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[var(--bg-primary)]/80 border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Award className="w-8 h-8 text-[var(--accent)] animate-pulse" />
          <div>
            <h1 className="text-xl font-bold tracking-tight text-[var(--text-primary)]">
              {common.courseTitle}
            </h1>
            <p className="text-xs text-[var(--text-secondary)] hidden sm:block">
              {common.completeCourse}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-[var(--border)] bg-[var(--bg-card)] hover:bg-[var(--bg-secondary)] text-xs font-semibold text-[var(--text-primary)] shadow-sm cursor-pointer"
          >
            <Globe className="w-4 h-4 text-[var(--accent)]" />
            {common.langSwitch}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 flex flex-col gap-10">
        
        {/* Welcome Hero Banner */}
        <section className="premium-card p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-8 border-l-4 border-l-[var(--accent)]">
          <div className="flex-1 flex flex-col gap-4">
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--accent)] bg-[var(--badge-bg)] w-max px-2.5 py-1 rounded">
              {common.completeCourse}
            </span>
            <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-[var(--text-primary)]">
              {common.courseSubtitle}
            </h2>
            <p className="text-sm md:text-base text-[var(--text-secondary)] max-w-xl leading-relaxed">
              {common.metaDesc}
            </p>
          </div>

          <div className="w-full md:w-80 flex flex-col gap-4 p-6 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border)] shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                {lang === "ru" ? "Ваш прогресс" : "Your Progress"}
              </span>
              <span className="text-xl font-black text-[var(--accent)]">
                {percentComplete}%
              </span>
            </div>
            
            <div className="w-full h-3.5 bg-[var(--border)] rounded-full overflow-hidden">
              <div
                className="h-full bg-[var(--accent)] progress-bar-fill rounded-full"
                style={{ width: `${percentComplete}%` }}
              />
            </div>

            <div className="mt-2 pt-3 border-t border-[var(--border)]">
              <div className="flex flex-col">
                <span className="text-[10px] uppercase font-bold text-[var(--text-secondary)]">
                  {lang === "ru" ? "Пройдено" : "Completed"}
                </span>
                <span className="text-sm font-black text-[var(--text-primary)]">
                  {completedCount} / {totalWeeksCount} {lang === "ru" ? "нед." : "weeks"}
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Filters */}
        <section className="flex flex-wrap items-center gap-2 pb-2 border-b border-[var(--border)]">
          <button
            onClick={() => setActiveMonth(null)}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer border ${
              activeMonth === null
                ? "bg-[var(--accent)] border-[var(--accent)] text-white shadow-sm"
                : "bg-[var(--bg-card)] border-[var(--border)] hover:bg-[var(--bg-secondary)] text-[var(--text-primary)]"
            }`}
          >
            {lang === "ru" ? "Все месяцы" : "All Months"}
          </button>
          
          {months.map((month) => (
            <button
              key={month}
              onClick={() => setActiveMonth(month)}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer border ${
                activeMonth === month
                  ? "bg-[var(--accent)] border-[var(--accent)] text-white shadow-sm"
                  : "bg-[var(--bg-card)] border-[var(--border)] hover:bg-[var(--bg-secondary)] text-[var(--text-primary)]"
              }`}
            >
              {getMonthName(month)}
            </button>
          ))}
        </section>

        {/* Roadmap Grid */}
        <section className="flex flex-col gap-10">
          {months
            .filter((m) => activeMonth === null || activeMonth === m)
            .map((month) => {
              const monthWeeks = weeksByMonth[month];
              return (
                <div key={month} className="flex flex-col gap-6 animate-fadeIn">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-extrabold tracking-tight text-[var(--text-primary)]">
                      {getMonthName(month)}
                    </h3>
                    <div className="h-[1px] flex-1 bg-[var(--border)]" />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {monthWeeks.map((week) => {
                      const weekId = `week-${week.weekNum}`;
                      const isCompleted = completedWeeks.includes(weekId);
                      
                      return (
                        <Link
                          key={week.weekNum}
                          href={`/${lang}/${weekId}`}
                          className={`premium-card p-6 flex flex-col justify-between hover:-translate-y-0.5 active:translate-y-0 cursor-pointer relative group ${
                            isCompleted ? "border-green-500/50 dark:border-green-500/30" : ""
                          }`}
                        >
                          <div className="flex flex-col gap-3">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-[var(--accent)] uppercase tracking-wider bg-[var(--badge-bg)] px-2 py-0.5 rounded">
                                {common.weekHeader} {week.weekNum}
                              </span>
                              
                              {isCompleted && (
                                <span className="flex items-center gap-1 text-[10px] font-bold text-green-600 dark:text-green-400 bg-green-500/10 px-2 py-0.5 rounded-full">
                                  <CheckCircle className="w-3.5 h-3.5" />
                                  {lang === "ru" ? "Пройдено" : "Completed"}
                                </span>
                              )}
                            </div>

                            <h4 className="text-base font-bold text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                              {week.title}
                            </h4>
                            
                            <p className="text-xs text-[var(--text-secondary)] leading-relaxed line-clamp-2">
                              {week.description}
                            </p>
                          </div>

                          <div className="flex items-center justify-between mt-6 pt-4 border-t border-[var(--border-light)] text-xs font-bold text-[var(--accent)]">
                            <span>{lang === "ru" ? "Изучить материалы" : "Study materials"}</span>
                            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })}
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[var(--border)] px-6 py-6 text-center text-[10px] uppercase font-bold tracking-wider text-[var(--text-secondary)] bg-[var(--bg-secondary)]">
        <p>
          © {new Date().getFullYear()} {common.courseTitle}. {common.allRightsReserved}.
        </p>
      </footer>
    </div>
  );
}
