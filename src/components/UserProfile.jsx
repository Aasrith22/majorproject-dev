import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BookOpen, CheckCircle2, Clock, TrendingUp } from "lucide-react";

// Mock user data - will be replaced with real backend data
const mockUserData = {
  name: "Student Name",
  email: "student@email.com",
  avatar: "",
  stats: {
    totalTests: 24,
    completed: 18,
    inProgress: 6,
    averageScore: 78,
  },
  recentTopics: [
    { id: 1, name: "Linear Algebra", progress: 85, status: "completed", score: 92 },
    { id: 2, name: "World History", progress: 60, status: "in-progress", score: 75 },
    { id: 3, name: "Organic Chemistry", progress: 45, status: "in-progress", score: 68 },
    { id: 4, name: "Classical Literature", progress: 100, status: "completed", score: 88 },
    { id: 5, name: "Data Structures", progress: 30, status: "in-progress", score: 71 },
  ],
};

export const UserProfile = () => {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="container mx-auto px-4">
        {/* Profile Header */}
        <div className="glass-card p-8 rounded-3xl mb-8 animate-slide-up">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <Avatar className="w-24 h-24 border-4 border-primary/20">
              <AvatarImage src={mockUserData.avatar} />
              <AvatarFallback className="text-2xl bg-gradient-to-br from-primary to-accent text-primary-foreground">
                {mockUserData.name.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-3xl font-bold mb-2">{mockUserData.name}</h2>
              <p className="text-muted-foreground">{mockUserData.email}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card p-4 rounded-xl text-center">
                <div className="text-2xl font-bold gradient-text">{mockUserData.stats.totalTests}</div>
                <div className="text-xs text-muted-foreground">Total Tests</div>
              </div>
              <div className="glass-card p-4 rounded-xl text-center">
                <div className="text-2xl font-bold gradient-text">{mockUserData.stats.averageScore}%</div>
                <div className="text-xs text-muted-foreground">Avg Score</div>
              </div>
            </div>
          </div>
        </div>

        {/* Topics List */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold">Your Learning Topics</h3>
            <div className="flex gap-2">
              <Badge variant="secondary" className="gap-1">
                <CheckCircle2 className="w-3 h-3" />
                {mockUserData.stats.completed} Completed
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Clock className="w-3 h-3" />
                {mockUserData.stats.inProgress} In Progress
              </Badge>
            </div>
          </div>

          <div className="grid gap-4">
            {mockUserData.recentTopics.map((topic, index) => (
              <Card 
                key={topic.id} 
                className="glass-card hover:scale-[1.02] transition-all duration-300"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{topic.name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {topic.status === 'completed' ? 'Completed' : 'In Progress'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-sm">
                        <TrendingUp className="w-4 h-4 text-primary" />
                        <span className="font-semibold">{topic.score}%</span>
                      </div>
                      <Badge 
                        variant={topic.status === 'completed' ? 'default' : 'secondary'}
                        className="mt-1"
                      >
                        {topic.status === 'completed' ? 'Complete' : 'Active'}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{topic.progress}%</span>
                    </div>
                    <Progress value={topic.progress} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
