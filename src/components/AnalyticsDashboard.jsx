import { Card } from "@/components/ui/card";

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
            <Card className="glass-card p-8 relative overflow-hidden group">
              <div className="space-y-6">
                {/* Analytics Preview Cards */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                    <div className="text-3xl font-bold gradient-text">87%</div>
                    <div className="text-sm text-muted-foreground">Avg Score</div>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                    <div className="text-3xl font-bold text-secondary">142</div>
                    <div className="text-sm text-muted-foreground">Questions</div>
                  </div>
                </div>
                
                {/* Progress Bars */}
                <div className="space-y-3">
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Data Structures</span>
                      <span className="text-muted-foreground">85%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[85%] rounded-full bg-gradient-to-r from-primary to-accent" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Algorithms</span>
                      <span className="text-muted-foreground">72%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[72%] rounded-full bg-gradient-to-r from-secondary to-accent" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>System Design</span>
                      <span className="text-muted-foreground">63%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[63%] rounded-full bg-gradient-to-r from-accent to-primary" />
                    </div>
                  </div>
                </div>
                
                {/* Chart placeholder */}
                <div className="h-32 rounded-lg border border-border/50 flex items-center justify-center">
                  <div className="flex items-end gap-2 h-20">
                    {[40, 65, 45, 80, 55, 90, 70].map((height, i) => (
                      <div
                        key={i}
                        className="w-6 rounded-t bg-gradient-to-t from-primary to-accent transition-all duration-500"
                        style={{ height: `${height}%`, animationDelay: `${i * 100}ms` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};
