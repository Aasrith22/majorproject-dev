import { Brain, Search, HelpCircle, MessageSquare, ArrowRight, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const agents = [
  {
    id: 1,
    icon: Brain,
    name: "Query Analysis Agent",
    description: "Understands intent using fine-tuned BERT model. Classifies questions as definitional, conceptual, or applied.",
    capabilities: ["Intent Classification", "Entity Extraction", "Context Understanding"],
    color: "from-purple-500 to-indigo-500",
  },
  {
    id: 2,
    icon: Search,
    name: "Information Retrieval Agent",
    description: "Combines semantic and keyword search using Sentence Transformers and Annoy index for fast retrieval.",
    capabilities: ["Semantic Search", "Keyword Matching", "Hybrid Retrieval"],
    color: "from-blue-500 to-cyan-500",
  },
  {
    id: 3,
    icon: HelpCircle,
    name: "Question Generation Agent",
    description: "Creates adaptive assessments using OpenAI & Gemini APIs. Analyzes multimodal student responses.",
    capabilities: ["Adaptive Questions", "Multimodal Analysis", "Response Evaluation"],
    color: "from-green-500 to-emerald-500",
  },
  {
    id: 4,
    icon: MessageSquare,
    name: "Feedback Agent",
    description: "Generates personalized improvement plans identifying strengths, weaknesses, and remediation strategies.",
    capabilities: ["Personalized Feedback", "Knowledge Gap Analysis", "Learning Path Updates"],
    color: "from-orange-500 to-yellow-500",
  },
];

export const AgentShowcase = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-primary/5 to-background" />
      
      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4 gap-2">
            <Sparkles className="w-3 h-3" />
            CrewAI Powered
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Four Specialized AI Agents</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our multi-agent orchestration system works in concert to deliver truly personalized adaptive learning
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {agents.map((agent, index) => {
            const Icon = agent.icon;
            return (
              <div key={agent.id} className="relative">
                <Card
                  className="glass-card p-6 h-full hover:scale-105 transition-all duration-300 group relative overflow-hidden"
                  style={{ animationDelay: `${index * 150}ms` }}
                >
                  {/* Agent Number */}
                  <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm font-bold z-10">
                    {agent.id}
                  </div>

                  {/* Glow effect */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  
                  <div className="relative z-10">
                    <div className={`w-14 h-14 mb-4 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center group-hover:animate-glow`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    
                    <h3 className="text-lg font-bold mb-2">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground mb-4">{agent.description}</p>
                    
                    {/* Capabilities */}
                    <div className="flex flex-wrap gap-1">
                      {agent.capabilities.map((cap) => (
                        <Badge key={cap} variant="outline" className="text-xs">
                          {cap}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </Card>

                {/* Arrow connector */}
                {index < agents.length - 1 && (
                  <div className="hidden lg:flex absolute top-1/2 -right-3 transform -translate-y-1/2 z-20">
                    <ArrowRight className="w-6 h-6 text-primary" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Workflow Description */}
        <Card className="glass-card p-8 max-w-4xl mx-auto">
          <h3 className="text-xl font-bold mb-4 text-center">
            Seamless Agent Orchestration
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary shrink-0">1</div>
                <p className="text-sm text-muted-foreground">Your query is analyzed for intent and context</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary shrink-0">2</div>
                <p className="text-sm text-muted-foreground">Relevant content is retrieved using hybrid search</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary shrink-0">3</div>
                <p className="text-sm text-muted-foreground">Adaptive questions generated based on your level</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary shrink-0">4</div>
                <p className="text-sm text-muted-foreground">Personalized feedback updates your learning path</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
};
