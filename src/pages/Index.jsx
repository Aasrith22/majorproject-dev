import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Brain,
  BookOpen,
  Code,
  Database,
  Network,
  Cpu,
  Binary,
  GitBranch,
  Search,
  Play,
  Clock,
  TrendingUp,
  Sparkles,
  ChevronRight,
  Star,
  Loader2,
} from "lucide-react";
import apiService from "@/services/unified-api.service.js";

// Default CS Course Topics - will be merged with custom topics from API
const defaultTopics = [
  {
    id: "data-structures-algorithms",
    name: "Data Structures & Algorithms",
    icon: GitBranch,
    description: "Arrays, Trees, Graphs, Sorting, Dynamic Programming",
    difficulty: "intermediate",
    progress: 45,
    color: "from-green-500 to-emerald-500",
    isCustom: false,
  },
  {
    id: "database-management",
    name: "Database Management Systems",
    icon: Database,
    description: "SQL, Normalization, Transactions, Indexing",
    difficulty: "intermediate",
    progress: 30,
    color: "from-blue-500 to-cyan-500",
    isCustom: false,
  },
  {
    id: "operating-systems",
    name: "Operating Systems",
    icon: Cpu,
    description: "Processes, Memory Management, File Systems, Scheduling",
    difficulty: "advanced",
    progress: 0,
    color: "from-purple-500 to-indigo-500",
    isCustom: false,
  },
  {
    id: "computer-networks",
    name: "Computer Networks",
    icon: Network,
    description: "OSI Model, TCP/IP, Routing, Network Security",
    difficulty: "intermediate",
    progress: 60,
    color: "from-orange-500 to-yellow-500",
    isCustom: false,
  },
  {
    id: "object-oriented-programming",
    name: "Object Oriented Programming",
    icon: Code,
    description: "Classes, Inheritance, Polymorphism, Design Patterns",
    difficulty: "beginner",
    progress: 85,
    color: "from-pink-500 to-rose-500",
    isCustom: false,
  },
  {
    id: "theory-of-computation",
    name: "Theory of Computation",
    icon: Binary,
    description: "Automata, Regular Languages, Turing Machines",
    difficulty: "advanced",
    progress: 15,
    color: "from-red-500 to-orange-500",
    isCustom: false,
  },
];

// Color palette for custom topics
const customTopicColors = [
  "from-cyan-500 to-blue-500",
  "from-violet-500 to-purple-500",
  "from-amber-500 to-orange-500",
  "from-teal-500 to-green-500",
  "from-rose-500 to-pink-500",
  "from-indigo-500 to-blue-500",
];

const Index = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [allTopics, setAllTopics] = useState(defaultTopics);
  const [filteredTopics, setFilteredTopics] = useState(defaultTopics);
  const [isLoading, setIsLoading] = useState(true);
  const [customTopicsCount, setCustomTopicsCount] = useState(0);

  // Load topics from API (includes custom topics)
  useEffect(() => {
    const loadTopics = async () => {
      try {
        setIsLoading(true);
        const apiTopics = await apiService.getTopics();
        
        // Merge API topics with default topics
        const mergedTopics = [...defaultTopics];
        let customCount = 0;
        
        // Add custom topics from API
        if (apiTopics && apiTopics.length > 0) {
          apiTopics.forEach((apiTopic, index) => {
            // Check if it's a custom topic not already in defaults
            const isInDefaults = defaultTopics.some(
              dt => dt.name.toLowerCase() === apiTopic.name.toLowerCase()
            );
            
            if (apiTopic.isCustom && !isInDefaults) {
              customCount++;
              mergedTopics.push({
                id: apiTopic.id,
                name: apiTopic.name,
                icon: Star, // Custom topics get a star icon
                description: apiTopic.description || `Custom topic: ${apiTopic.name}`,
                difficulty: apiTopic.difficulty || "intermediate",
                progress: apiTopic.sessionsCompleted > 0 ? Math.min(apiTopic.sessionsCompleted * 20, 100) : 0,
                color: customTopicColors[index % customTopicColors.length],
                isCustom: true,
                sessionsCompleted: apiTopic.sessionsCompleted || 0,
                lastStudied: apiTopic.lastStudied,
              });
            }
          });
        }
        
        setAllTopics(mergedTopics);
        setFilteredTopics(mergedTopics);
        setCustomTopicsCount(customCount);
      } catch (error) {
        console.error("Failed to load topics:", error);
        setAllTopics(defaultTopics);
        setFilteredTopics(defaultTopics);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadTopics();
  }, []);

  // Filter topics based on search
  useEffect(() => {
    const filtered = allTopics.filter(
      (topic) =>
        topic.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        topic.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredTopics(filtered);
  }, [searchQuery, allTopics]);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "beginner":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "intermediate":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "advanced":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-24 pb-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5" />
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 glass-card rounded-full">
              <Sparkles className="w-4 h-4 text-secondary" />
              <span className="text-sm font-medium">AI-Powered Adaptive Learning</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Welcome to <span className="gradient-text">EduSynapse</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Select a topic below to start your personalized learning session
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-xl mx-auto mb-8">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 h-12 text-lg bg-background/50 border-border/50"
              />
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex justify-center gap-6 mb-12">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <BookOpen className="w-4 h-4 text-primary" />
              <span>{allTopics.length} Courses Available</span>
            </div>
            {customTopicsCount > 0 && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Star className="w-4 h-4 text-yellow-400" />
                <span>{customTopicsCount} Custom Topics</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span>{allTopics.filter(t => t.progress > 0).length} In Progress</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4 text-secondary" />
              <span>~30 min sessions</span>
            </div>
          </div>
        </div>
      </section>

      {/* Topics Grid */}
      <section className="pb-24">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="glass-card p-6">
                  <div className="flex items-start justify-between mb-4">
                    <Skeleton className="w-12 h-12 rounded-xl" />
                    <Skeleton className="w-20 h-6 rounded-full" />
                  </div>
                  <Skeleton className="h-6 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full mb-4" />
                  <Skeleton className="h-2 w-full" />
                </Card>
              ))}
            </div>
          ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTopics.map((topic) => {
              const Icon = topic.icon;
              return (
                <Card
                  key={topic.id}
                  className="glass-card p-6 hover:scale-[1.02] transition-all duration-300 cursor-pointer group relative"
                  onClick={() => navigate(`/learn?topic=${encodeURIComponent(topic.name)}`)}
                >
                  {/* Custom Topic Badge */}
                  {topic.isCustom && (
                    <Badge className="absolute top-2 right-2 bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      <Star className="w-3 h-3 mr-1" />
                      Custom
                    </Badge>
                  )}
                  
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-12 h-12 rounded-xl bg-gradient-to-br ${topic.color} flex items-center justify-center group-hover:animate-glow`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    {!topic.isCustom && (
                      <Badge
                        variant="outline"
                        className={getDifficultyColor(topic.difficulty)}
                      >
                        {topic.difficulty}
                      </Badge>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                    {topic.name}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {topic.description}
                  </p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        {topic.isCustom ? "Sessions" : "Progress"}
                      </span>
                      <span className="font-medium">
                        {topic.isCustom ? (topic.sessionsCompleted || 0) : `${topic.progress}%`}
                      </span>
                    </div>
                    {!topic.isCustom && <Progress value={topic.progress} className="h-2" />}
                    {topic.isCustom && topic.lastStudied && (
                      <p className="text-xs text-muted-foreground">
                        Last studied: {new Date(topic.lastStudied).toLocaleDateString()}
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-border/50 flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      {topic.isCustom ? "Practice Again" : (topic.progress > 0 ? "Continue Learning" : "Start Learning")}
                    </span>
                    <Button size="sm" variant="ghost" className="gap-1 group-hover:text-primary">
                      <Play className="w-4 h-4" />
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
          )}

          {filteredTopics.length === 0 && (
            <div className="text-center py-12">
              <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No topics found</h3>
              <p className="text-muted-foreground">
                Try searching with different keywords
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Index;
