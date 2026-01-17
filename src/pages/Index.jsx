import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
  Sparkles,
  ChevronRight,
  Star,
} from "lucide-react";
import apiService from "@/services/unified-api.service.js";

// Default CS Course Topics - will be merged with custom topics from API
const defaultTopics = [
  {
    id: "data-structures-algorithms",
    name: "Data Structures & Algorithms",
    icon: GitBranch,
    description: "Arrays, Trees, Graphs, Sorting, Dynamic Programming",
    color: "from-green-500 to-emerald-500",
    isCustom: false,
  },
  {
    id: "database-management",
    name: "Database Management Systems",
    icon: Database,
    description: "SQL, Normalization, Transactions, Indexing",
    color: "from-blue-500 to-cyan-500",
    isCustom: false,
  },
  {
    id: "operating-systems",
    name: "Operating Systems",
    icon: Cpu,
    description: "Processes, Memory Management, File Systems, Scheduling",
    color: "from-purple-500 to-indigo-500",
    isCustom: false,
  },
  {
    id: "computer-networks",
    name: "Computer Networks",
    icon: Network,
    description: "OSI Model, TCP/IP, Routing, Network Security",
    color: "from-orange-500 to-yellow-500",
    isCustom: false,
  },
  {
    id: "object-oriented-programming",
    name: "Object Oriented Programming",
    icon: Code,
    description: "Classes, Inheritance, Polymorphism, Design Patterns",
    color: "from-pink-500 to-rose-500",
    isCustom: false,
  },
  {
    id: "theory-of-computation",
    name: "Theory of Computation",
    icon: Binary,
    description: "Automata, Regular Languages, Turing Machines",
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
                color: customTopicColors[index % customTopicColors.length],
                isCustom: true,
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

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-24 pb-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5" />
        <div className="absolute top-20 left-1/4 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-secondary/10 rounded-full blur-3xl" />
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-2xl mx-auto text-center mb-8">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 mb-4 glass-card rounded-full">
              <Sparkles className="w-4 h-4 text-secondary" />
              <span className="text-sm font-medium">AI-Powered Adaptive Learning</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-3">
              Welcome to <span className="gradient-text">EduSynapse</span>
            </h1>
            <p className="text-muted-foreground">
              Select a topic to start your personalized learning session
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-md mx-auto mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-10 bg-background/50 border-border/50"
              />
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex justify-center gap-4 mb-8">
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <BookOpen className="w-4 h-4 text-primary" />
              <span>{allTopics.length} Courses</span>
            </div>
            {customTopicsCount > 0 && (
              <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <Star className="w-4 h-4 text-yellow-400" />
                <span>{customTopicsCount} Custom Topics</span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Topics Grid */}
      <section className="pb-24">
        <div className="container mx-auto px-4">
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="glass-card p-5">
                  <div className="flex items-center gap-4 mb-3">
                    <Skeleton className="w-10 h-10 rounded-lg" />
                    <Skeleton className="h-5 w-2/3" />
                  </div>
                  <Skeleton className="h-4 w-full" />
                </Card>
              ))}
            </div>
          ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredTopics.map((topic) => {
              const Icon = topic.icon;
              return (
                <Card
                  key={topic.id}
                  className="glass-card p-5 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-200 cursor-pointer group"
                  onClick={() => navigate(`/learn?topic=${encodeURIComponent(topic.name)}`)}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-10 h-10 rounded-lg bg-gradient-to-br ${topic.color} flex items-center justify-center flex-shrink-0`}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold truncate group-hover:text-primary transition-colors">
                          {topic.name}
                        </h3>
                        {topic.isCustom && (
                          <Star className="w-3.5 h-3.5 text-yellow-400 flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {topic.description}
                      </p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
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
