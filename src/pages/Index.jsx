import { Hero } from "@/components/Hero";
import { UserProfile } from "@/components/UserProfile";
import { Features } from "@/components/Features";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";
import { HowItWorks } from "@/components/HowItWorks";
import { CTASection } from "@/components/CTASection";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <UserProfile />
      <HowItWorks />
      <Features />
      <AnalyticsDashboard />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;
