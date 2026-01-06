import { Button } from "@/components/ui/button";
import { BookOpen, LayoutDashboard } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const CTASection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-3xl animate-glow" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass-card p-12 rounded-3xl">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Start Your{" "}
              <span className="gradient-text">Learning Journey</span>
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Experience adaptive learning powered by AI agents that understand your unique learning style
            </p>
            
            <div className="flex gap-4 justify-center flex-wrap">
              <Button 
                size="lg"
                className="bg-gradient-to-r from-primary to-accent hover:shadow-lg hover:shadow-primary/50 transition-all duration-300"
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
                View Progress
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
