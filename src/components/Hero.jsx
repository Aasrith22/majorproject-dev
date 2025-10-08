import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles } from "lucide-react";
import heroBg from "@/assets/hero-bg.jpg";

export const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />
      
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
      <div className="relative z-10 container mx-auto px-4 text-center animate-slide-up">
        <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 glass-card rounded-full">
          <Sparkles className="w-4 h-4 text-secondary" />
          <span className="text-sm font-medium">AI-Powered Learning Platform</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
          Master Any Subject with{" "}
          <span className="gradient-text">EduSynapse</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
          Adaptive learning platform that personalizes your study experience, tracks your progress, and helps you achieve mastery
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button 
            size="lg" 
            className="group bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-primary/50 transition-all duration-300"
          >
            Start Learning
            <BookOpen className="ml-2 w-4 h-4" />
          </Button>
          <Button 
            size="lg" 
            variant="outline"
            className="border-primary/50 hover:bg-primary/10"
          >
            Browse Topics
          </Button>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">500+</div>
            <div className="text-sm text-muted-foreground mt-1">Topics Available</div>
          </div>
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">85%</div>
            <div className="text-sm text-muted-foreground mt-1">Average Improvement</div>
          </div>
          <div className="glass-card p-6 rounded-2xl hover:scale-105 transition-transform duration-300">
            <div className="text-3xl font-bold gradient-text">24/7</div>
            <div className="text-sm text-muted-foreground mt-1">Personalized Learning</div>
          </div>
        </div>
      </div>
    </section>
  );
};
