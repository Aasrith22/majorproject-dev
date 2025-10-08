import { Upload, Zap, BarChart, Trophy } from "lucide-react";
import { Card } from "@/components/ui/card";

const steps = [
  {
    icon: Upload,
    title: "Choose Your Topic",
    description: "Browse subjects or upload your study materials to get started",
    step: "01",
  },
  {
    icon: Zap,
    title: "Take Adaptive Tests",
    description: "Experience personalized assessments that adjust to your skill level",
    step: "02",
  },
  {
    icon: BarChart,
    title: "Track Progress",
    description: "View detailed insights on your performance and knowledge gaps",
    step: "03",
  },
  {
    icon: Trophy,
    title: "Achieve Mastery",
    description: "Follow personalized learning paths and reach your educational goals",
    step: "04",
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-float-delayed" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Your <span className="gradient-text">Learning Path</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Four steps to mastery with personalized, adaptive learning
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {/* Connection line for desktop */}
          <div className="hidden lg:block absolute top-1/4 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
          
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <Card
                key={step.title}
                className="glass-card p-6 hover:scale-105 transition-all duration-300 relative"
                style={{
                  animationDelay: `${index * 150}ms`,
                }}
              >
                {/* Step number badge */}
                <div className="absolute -top-4 -right-4 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-lg font-bold shadow-lg animate-glow">
                  {step.step}
                </div>
                
                <div className="mb-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                    <Icon className="w-7 h-7 text-primary" />
                  </div>
                </div>
                
                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
