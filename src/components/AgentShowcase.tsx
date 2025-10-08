import { Brain, LineChart, Target } from "lucide-react";
import { Card } from "@/components/ui/card";

const agents = [
  {
    icon: Brain,
    name: "Assessment Agent",
    description: "Generates adaptive, personalized tests tailored to individual learning needs",
    color: "from-primary to-accent",
  },
  {
    icon: LineChart,
    name: "Analysis Agent",
    description: "Identifies strengths and weaknesses through in-depth performance analysis",
    color: "from-accent to-secondary",
  },
  {
    icon: Target,
    name: "Feedback Agent",
    description: "Creates personalized improvement plans with progress tracking and reminders",
    color: "from-secondary to-primary",
  },
];

export const AgentShowcase = () => {
  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 animate-slide-up">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Powered by <span className="gradient-text">Multi-Agent AI</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Three specialized AI agents work in harmony to deliver personalized learning experiences
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {agents.map((agent, index) => {
            const Icon = agent.icon;
            return (
              <Card
                key={agent.name}
                className="glass-card p-8 hover:scale-105 transition-all duration-300 group relative overflow-hidden"
                style={{
                  animationDelay: `${index * 200}ms`,
                }}
              >
                {/* Glow effect */}
                <div className={`absolute inset-0 bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                
                <div className="relative z-10">
                  <div className={`w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br ${agent.color} p-0.5 animate-glow`}>
                    <div className="w-full h-full bg-card rounded-2xl flex items-center justify-center">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-3">{agent.name}</h3>
                  <p className="text-muted-foreground">{agent.description}</p>
                </div>
              </Card>
            );
          })}
        </div>
        
        {/* Connection lines visualization */}
        <div className="relative mt-12 h-32 hidden md:block">
          <svg className="w-full h-full absolute" style={{ top: -100 }}>
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="hsl(263 70% 62%)" stopOpacity="0.3" />
                <stop offset="50%" stopColor="hsl(189 94% 43%)" stopOpacity="0.5" />
                <stop offset="100%" stopColor="hsl(263 70% 62%)" stopOpacity="0.3" />
              </linearGradient>
            </defs>
            <path
              d="M 20,50 Q 200,10 400,50 T 780,50"
              stroke="url(#lineGradient)"
              strokeWidth="2"
              fill="none"
              className="animate-pulse"
            />
          </svg>
        </div>
      </div>
    </section>
  );
};
