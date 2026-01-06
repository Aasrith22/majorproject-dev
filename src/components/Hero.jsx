import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles, LayoutDashboard } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-primary/5 to-background" />
      
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
      
      {/* Animated particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-primary rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              opacity: 0.3 + Math.random() * 0.4,
            }}
          />
        ))}
      </div>
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 text-center animate-slide-up pt-16">
        <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 glass-card rounded-full">
          <Sparkles className="w-4 h-4 text-secondary" />
          <span className="text-sm font-medium">AI-Powered Adaptive Learning Platform</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
          Master Any Subject with{" "}
          <span className="gradient-text">EduSynapse</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
          Experience personalized learning powered by four specialized AI agents that adapt to your unique learning style and pace
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button 
            size="lg" 
            className="group bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-primary/50 transition-all duration-300"
            onClick={() => navigate("/learn")}
          >
            Start Learning
            <BookOpen className="ml-2 w-4 h-4" />
          </Button>
          <Button 
            size="lg" 
            variant="outline"
            className="border-primary/50 hover:bg-primary/10"
            onClick={() => navigate("/dashboard")}
          >
            <LayoutDashboard className="mr-2 w-4 h-4" />
            View Dashboard
          </Button>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">4</div>
            <div className="text-sm text-muted-foreground mt-1">AI Agents</div>
          </div>
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">3</div>
            <div className="text-sm text-muted-foreground mt-1">Input Modes</div>
          </div>
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">24/7</div>
            <div className="text-sm text-muted-foreground mt-1">Adaptive Learning</div>
          </div>
        </div>
      </div>
    </section>
  );
};
