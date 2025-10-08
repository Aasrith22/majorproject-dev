import { Card } from "@/components/ui/card";
import analyticsVisual from "@/assets/analytics-visual.jpg";

export const AnalyticsDashboard = () => {
  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="animate-slide-up">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Real-Time{" "}
              <span className="gradient-text">Performance Analytics</span>
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Track learning progress with comprehensive insights and data-driven recommendations
            </p>
            
            <div className="space-y-4">
              <Card className="glass-card p-4 hover:scale-105 transition-transform duration-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                  <div>
                    <div className="font-semibold">Adaptive Testing Engine</div>
                    <div className="text-sm text-muted-foreground">Dynamic difficulty adjustment in real-time</div>
                  </div>
                </div>
              </Card>
              
              <Card className="glass-card p-4 hover:scale-105 transition-transform duration-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
                  <div>
                    <div className="font-semibold">Strength & Weakness Analysis</div>
                    <div className="text-sm text-muted-foreground">Identify knowledge gaps automatically</div>
                  </div>
                </div>
              </Card>
              
              <Card className="glass-card p-4 hover:scale-105 transition-transform duration-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                  <div>
                    <div className="font-semibold">Personalized Improvement Plans</div>
                    <div className="text-sm text-muted-foreground">Custom learning paths with progress tracking</div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
          
          <div className="relative animate-slide-in-right">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-3xl blur-3xl" />
            <Card className="glass-card p-2 relative overflow-hidden group">
              <img 
                src={analyticsVisual} 
                alt="Analytics Dashboard" 
                className="w-full h-auto rounded-2xl group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};
