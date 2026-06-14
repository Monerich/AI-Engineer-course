import React from "react";
import fs from "fs";
import path from "path";
import { marked } from "marked";
import WeekDetailClient from "../../../components/WeekDetailClient";

const WEEKS_WITHOUT_LOCALIZED_MEDIA = new Set(["week-2"]);

interface PageProps {
  params: Promise<{
    lang: string;
    week: string;
  }>;
}

export async function generateStaticParams() {
  const paths = [];
  const languages = ["ru", "en"];
  for (const lang of languages) {
    for (let i = 1; i <= 26; i++) {
      paths.push({ lang, week: `week-${i}` });
    }
  }
  return paths;
}

// Robust cleanup function for NotebookLM output
function cleanNotebookLmMarkdown(rawContent: string): string {
  let content = rawContent.trim();
  
  // 1. Unpack JSON wrapping (even if preceded by a title header)
  const firstBrace = content.indexOf("{");
  const lastBrace = content.lastIndexOf("}");
  
  if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
    const potentialJson = content.substring(firstBrace, lastBrace + 1);
    try {
      const parsed = JSON.parse(potentialJson);
      const answer = parsed.value?.answer || parsed.answer || "";
      if (answer) {
        content = answer.trim();
      }
    } catch {
      // Ignore JSON error, keep raw content
    }
  }
  
  // Replace specific PDF filenames with human-readable localized phrases
  const isEn = content.includes("Block 1") || content.includes("Block 2") || content.includes("Scene 1");
  const pdfReplacements: Record<string, string> = isEn ? {
    "agent_roadmap_ru\\.pdf": "AI Agent roadmap",
    "ai_builder_ru\\.pdf": "AI Engineer roadmap",
    "50_automations_ru\\.pdf": "automations guide",
    "AI_Money_Hunter_RU\\.pdf": "AI monetization guide",
    "5_pipelines_ru\\.pdf": "pipelines guide",
    "ai_trends_ru\\.pdf": "AI trends analysis",
    "Learn Harness Engineering": "Harness Engineering course"
  } : {
    "agent_roadmap_ru\\.pdf": "карта развития ИИ-Агентов",
    "ai_builder_ru\\.pdf": "карта развития ИИ-Инженера",
    "50_automations_ru\\.pdf": "руководство по автоматизации",
    "AI_Money_Hunter_RU\\.pdf": "руководство по монетизации ИИ",
    "5_pipelines_ru\\.pdf": "руководство по конвейерам данных",
    "ai_trends_ru\\.pdf": "анализ трендов ИИ",
    "Learn Harness Engineering": "курс по Harness-инженерии"
  };

  for (const [pattern, replacement] of Object.entries(pdfReplacements)) {
    content = content.replace(new RegExp(pattern, "gi"), replacement);
  }

  // Remove any remaining generic .pdf filenames (strip extension)
  content = content.replace(/\b([a-zA-Z0-9_-]+)\.pdf\b/gi, "$1");
  
  // 2. Strip bracketed footnotes like [1], [2], [1, 2]
  content = content.replace(/\[\d+(?:,\s*\d+)*\]/g, "");
  // Strip separated footnotes like [1] , [2]
  content = content.replace(/\[\d+\]\s*,\s*\[\d+\]/g, "");
  // Clean double spaces
  content = content.replace(/ +/g, " ");
  // Clean spaces before punctuation
  content = content.replace(/\s+([.,!?;:])/g, "$1");
  
  return content.trim();
}

export default async function Page({ params }: PageProps) {
  const { lang, week } = await params;
  const validatedLang = lang === "en" ? "en" : "ru";

  let lectureHtml = "";
  let slidesHtml = "";
  let videoHtml = "";

  try {
    const baseDir = path.join(process.cwd(), "src", "data", "lessons", validatedLang, week);
    
    // Load and compile lecture
    const lecturePath = path.join(baseDir, "lecture.md");
    if (fs.existsSync(lecturePath)) {
      const rawContent = fs.readFileSync(lecturePath, "utf-8");
      const cleanMarkdown = cleanNotebookLmMarkdown(rawContent);
      lectureHtml = await marked.parse(cleanMarkdown);
      // Add navigable IDs to block headings in any format:
      // "## Блок N:" / "## Block N:" / "## N. Блок N (...)" (NotebookLM JSON output)
      lectureHtml = lectureHtml.replace(
        /<h2>((?:\d+\.\s+)?(?:Блок|Block)\s+(\d+)[\s:(])/g,
        (_match, text, num) => `<h2 id="lecture-block-${num}">${text}`
      );
    }

    // Load markdown fallback for slides when native PDF assets are not deployed.
    const slidesPath = path.join(baseDir, "slides.md");
    if (fs.existsSync(slidesPath)) {
      const rawContent = fs.readFileSync(slidesPath, "utf-8");
      const cleanMarkdown = cleanNotebookLmMarkdown(rawContent);
      slidesHtml = await marked.parse(cleanMarkdown);
    }

    // Load markdown fallback for video when native MP4 assets are not deployed.
    const videoPath = path.join(baseDir, "video.md");
    if (fs.existsSync(videoPath)) {
      const rawContent = fs.readFileSync(videoPath, "utf-8");
      const cleanMarkdown = cleanNotebookLmMarkdown(rawContent);
      videoHtml = await marked.parse(cleanMarkdown);
    }
  } catch (error) {
    console.error(`Error loading or compiling lesson materials for ${week}:`, error);
  }

  // Check if native slide PDF exists
  const slidesPdfLangPath = path.join(process.cwd(), "public", "lessons", week, validatedLang, "slides.pdf");
  const slidesPdfRootPath = path.join(process.cwd(), "public", "lessons", week, "slides.pdf");
  const slidesPdfUrl = fs.existsSync(slidesPdfLangPath)
    ? `/lessons/${week}/${validatedLang}/slides.pdf`
    : (fs.existsSync(slidesPdfRootPath) ? `/lessons/${week}/slides.pdf` : undefined);

  // Check if native video MP4 exists
  const videoMp4LangPath = path.join(process.cwd(), "public", "lessons", week, validatedLang, "video.mp4");
  const videoMp4RootPath = path.join(process.cwd(), "public", "lessons", week, "video.mp4");
  const videoMp4Url = fs.existsSync(videoMp4LangPath)
    ? `/lessons/${week}/${validatedLang}/video.mp4`
    : (fs.existsSync(videoMp4RootPath) ? `/lessons/${week}/video.mp4` : undefined);
  const mediaBaseUrl = process.env.LESSON_MEDIA_BASE_URL?.replace(/\/$/, "");
  const remoteMediaLangSegment = validatedLang === "en" && !WEEKS_WITHOUT_LOCALIZED_MEDIA.has(week) ? "/en" : "";
  const remoteSlidesPdfUrl = mediaBaseUrl ? `${mediaBaseUrl}/lessons/${week}${remoteMediaLangSegment}/slides.pdf` : undefined;
  const remoteVideoMp4Url = mediaBaseUrl ? `${mediaBaseUrl}/lessons/${week}${remoteMediaLangSegment}/video.mp4` : undefined;

  return (
    <WeekDetailClient 
      key={week}
      lang={validatedLang}
      weekId={week}
      lectureHtml={lectureHtml}
      slidesHtml={slidesHtml}
      videoHtml={videoHtml}
      slidesPdfUrl={slidesPdfUrl || remoteSlidesPdfUrl}
      videoMp4Url={videoMp4Url || remoteVideoMp4Url}
    />
  );
}
