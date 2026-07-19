"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useSettings } from "@/components/theme-provider";
import { ONBOARDING_VERSION } from "@/lib/onboarding";

export function OnboardingGate() {
  const { settings } = useSettings();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!settings) return;
    if (pathname.startsWith("/onboarding")) return;
    if (settings.onboarding_seen_version !== ONBOARDING_VERSION) {
      router.replace("/onboarding");
    }
  }, [settings, pathname, router]);

  return null;
}