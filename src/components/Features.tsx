import { BookOpen, Zap, Users, Shield, TrendingUp, Globe } from "lucide-react";
import { Card } from "@/components/ui/card";

const features = [
  {
    icon: BookOpen,
    title: "Multi-Modal Input",
    description: "Support for text, handwriting, diagrams, and voice inputs",
  },
  {
    icon: Zap,
    title: "Real-Time Adaptation",
    description: "Dynamic difficulty adjustment based on performance",
  },
  {
    icon: Users,
    title: "Personalized Learning",
    description: "Tailored improvement plans for each student",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Enterprise-grade security and data protection",
  },
  {
    icon: TrendingUp,
    title: "Progress Tracking",
    description: "Comprehensive analytics and performance insights",
  },
  {
    icon: Globe,
    title: "Web Integration",
    description: "Seamless integration with online content and resources",
  },
];

export const Features = () => {
  return (
    <section className="py-24 relative">
      {/* Background gradient blob */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-3xl" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Comprehensive Features</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need for next-generation personalized education
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={feature.title}
                className="glass-card p-6 hover:scale-105 transition-all duration-300 group cursor-pointer"
                style={{
                  animationDelay: `${index * 100}ms`,
                }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 group-hover:animate-glow">
                    <Icon className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
