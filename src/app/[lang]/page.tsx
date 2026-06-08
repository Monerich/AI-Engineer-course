import React from "react";
import DashboardClient from "../../components/DashboardClient";

interface PageProps {
  params: Promise<{
    lang: string;
  }>;
}

export async function generateStaticParams() {
  return [{ lang: "ru" }, { lang: "en" }];
}

export default async function Page({ params }: PageProps) {
  const { lang } = await params;
  const validatedLang = lang === "en" ? "en" : "ru";

  return <DashboardClient lang={validatedLang} />;
}
