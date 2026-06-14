import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Automation & AI Agent Builder Course",
  description: "Become an AI Automation Specialist and Agent Developer in 6 months. High-impact curriculum with practical n8n and Python projects.",
};

export default async function LanguageLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  await params;

  return (
    <div className={`${geistSans.variable} ${geistMono.variable} min-h-screen flex flex-col font-sans`}>
      {children}
    </div>
  );
}
