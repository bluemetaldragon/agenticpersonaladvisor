import { AppShell } from "@/components/shell/app-shell";
import { OnboardingGate } from "@/components/onboarding-gate";

export default function AppGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <OnboardingGate />
      <AppShell>{children}</AppShell>
    </>
  );
}