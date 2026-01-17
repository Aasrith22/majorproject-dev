import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  BookOpen,
  TrendingUp,
  Target,
  Clock,
  CheckCircle2,
  Flame,
  Award,
  Brain,
  AlertTriangle,
  ChevronRight,
  Play,
  Calendar,
  Zap,
} from "lucide-react";
import apiService from "@/services/unified-api.service.js";

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [learnerProfile, setLearnerProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const [dashboard, profile, learner] = await Promise.all([
          apiService.getDashboardData(),
          apiService.getUserProfile(),
          apiService.getLearnerProfile(),
        ]);
        setDashboardData(dashboard);
        setUserProfile(profile);
        setLearnerProfile(learner);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  if (isLoading || !dashboardData || !userProfile) {
    return (
      <AppLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-pulse text-center">
            <Brain className="w-12 h-12 text-primary mx-auto mb-4 animate-spin" />
            <p className="text-muted-foreground">Loading your dashboard...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  const { stats, recentTopics, learningPath } = userProfile;
  const { performanceHistory = [], conceptMastery = [] } = dashboardData || {};

  // Check if user has any data
  const hasData = stats.questionsAnswered > 0 || stats.completedSessions > 0;

  // Prepare radar chart data - show helpful message when no data
  const radarData = conceptMastery.length > 0 
    ? conceptMastery.map((c) => ({
        concept: c.concept?.split(" ")[0] || "Unknown",
        mastery: c.mastery || 0,
        fullMark: 100,
      }))
    : null; // Return null to show empty state instead of fake data

  // Ensure performanceHistory has data for charts
  const chartPerformanceHistory = performanceHistory.length > 0
    ? performanceHistory
    : null; // Return null to show empty state

  return (
    <AppLayout showFooter={false}>
      <div className="min-h-screen bg-gradient-to-b from-background to-background/95">
        <div className="container mx-auto px-4 py-8">
          {/* Profile Header */}
          <div className="glass-card p-6 rounded-2xl mb-8">
            <div className="flex flex-col lg:flex-row items-center gap-6">
              <Avatar className="w-20 h-20 border-4 border-primary/20">
                <AvatarImage src={userProfile.user.avatar} />
                <AvatarFallback className="text-2xl bg-gradient-to-br from-primary to-accent text-primary-foreground">
                  {userProfile.user.name.split(" ").map((n) => n[0]).join("")}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 text-center lg:text-left">
                <h1 className="text-2xl font-bold mb-1">{userProfile.user.name}</h1>
                <p className="text-muted-foreground">{userProfile.user.email}</p>
                <div className="flex items-center justify-center lg:justify-start gap-2 mt-2">
                  <Badge variant="secondary" className="gap-1">
                    <Flame className="w-3 h-3 text-orange-400" />
                    {stats.streakDays} day streak
                  </Badge>
                  <Badge variant="outline" className="gap-1">
                    <Award className="w-3 h-3 text-primary" />
                    {stats.completedSessions} sessions completed
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <StatCard icon={CheckCircle2} label="Questions" value={stats.questionsAnswered.toString()} color="text-blue-400" />
                <StatCard icon={Clock} label="Time Spent" value={`${Math.floor(stats.totalTimeSpent / 60)}h`} color="text-purple-400" />
              </div>
            </div>
          </div>

          {/* Main Content */}
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="glass-card">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="progress">Progress</TabsTrigger>
              <TabsTrigger value="topics">Topics</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              {/* Empty State for New Users */}
              {!hasData && (
                <Card className="glass-card p-8">
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                      <BookOpen className="w-8 h-8 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold">Welcome to Your Learning Dashboard!</h3>
                    <p className="text-muted-foreground max-w-md mx-auto">
                      Start your first learning session to see your analytics, track progress, and get personalized insights.
                    </p>
                    <Button onClick={() => navigate("/")} className="gap-2">
                      <Play className="w-4 h-4" />
                      Start Learning
                    </Button>
                  </div>
                </Card>
              )}

              {hasData && (
                <>
                  <div className="grid lg:grid-cols-3 gap-6">
                    {/* Performance Chart */}
                    <Card className="glass-card lg:col-span-2">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <TrendingUp className="w-5 h-5 text-primary" />
                          Performance Over Time
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {chartPerformanceHistory ? (
                          <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={chartPerformanceHistory}>
                              <defs>
                                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="hsl(263 70% 62%)" stopOpacity={0.3} />
                                  <stop offset="95%" stopColor="hsl(263 70% 62%)" stopOpacity={0} />
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 15% 25%)" />
                              <XAxis
                                dataKey="date"
                                stroke="hsl(215 20.2% 65.1%)"
                                fontSize={12}
                                tickFormatter={(value) => new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                              />
                              <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} domain={[0, 100]} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: "hsl(220 20% 12%)",
                                  border: "1px solid hsl(220 15% 25%)",
                                  borderRadius: "8px",
                                }}
                              />
                              <Area type="monotone" dataKey="score" stroke="hsl(263 70% 62%)" strokeWidth={2} fill="url(#scoreGradient)" />
                            </AreaChart>
                          </ResponsiveContainer>
                        ) : (
                          <div className="h-[300px] flex items-center justify-center">
                            <div className="text-center">
                              <TrendingUp className="w-12 h-12 text-muted-foreground/30 mx-auto mb-2" />
                              <p className="text-muted-foreground">Complete sessions to see your performance trends</p>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Concept Mastery Radar */}
                    <Card className="glass-card">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Brain className="w-5 h-5 text-secondary" />
                          Concept Mastery
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {radarData ? (
                          <ResponsiveContainer width="100%" height={250}>
                            <RadarChart data={radarData}>
                              <PolarGrid stroke="hsl(220 15% 25%)" />
                              <PolarAngleAxis dataKey="concept" tick={{ fill: "hsl(215 20.2% 65.1%)", fontSize: 10 }} />
                              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "hsl(215 20.2% 65.1%)", fontSize: 10 }} />
                              <Radar name="Mastery" dataKey="mastery" stroke="hsl(189 94% 43%)" fill="hsl(189 94% 43%)" fillOpacity={0.3} />
                            </RadarChart>
                          </ResponsiveContainer>
                        ) : (
                          <div className="h-[250px] flex items-center justify-center">
                            <div className="text-center">
                              <Brain className="w-12 h-12 text-muted-foreground/30 mx-auto mb-2" />
                              <p className="text-sm text-muted-foreground">Practice topics to track mastery</p>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </>
              )}

              {/* Quick Actions & Recent Topics - Only show when user has some activity */}
              {(hasData || recentTopics.length > 0 || learningPath.recommendedTopics?.length > 0) && (
                <div className="grid lg:grid-cols-3 gap-6">
                  {/* Continue Learning */}
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Play className="w-5 h-5 text-green-400" />
                        Continue Learning
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {learningPath.currentTopic ? (
                        <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                          <h4 className="font-semibold mb-2">{learningPath.currentTopic.name}</h4>
                          <div className="flex items-center gap-2 mb-3">
                            <Progress value={learningPath.currentTopic.progress} className="flex-1 h-2" />
                            <span className="text-sm text-muted-foreground">{learningPath.currentTopic.progress}%</span>
                          </div>
                          <Button className="w-full gap-2" onClick={() => navigate(`/learn?topic=${learningPath.currentTopic?.id}`)}>
                            <Play className="w-4 h-4" />
                            Resume
                          </Button>
                        </div>
                      ) : (
                        <div className="p-4 rounded-lg bg-muted/20 border border-border/50 text-center">
                          <p className="text-sm text-muted-foreground">Start a session to track progress</p>
                          <Button variant="outline" className="mt-2" onClick={() => navigate("/")}>
                            Browse Topics
                          </Button>
                        </div>
                      )}

                      {learningPath.recommendedTopics?.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-muted-foreground">Recommended Next:</p>
                          {learningPath.recommendedTopics.slice(0, 2).map((topic) => (
                            <Button key={topic.id} variant="outline" className="w-full justify-between" onClick={() => navigate(`/learn?topic=${topic.id}`)}>
                              <span>{topic.name}</span>
                              <ChevronRight className="w-4 h-4" />
                            </Button>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Knowledge Gaps */}
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-orange-400" />
                        Knowledge Gaps
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-[200px]">
                        {learningPath.knowledgeGaps?.length > 0 ? (
                          <div className="space-y-3">
                            {learningPath.knowledgeGaps.map((gap) => (
                              <div key={gap.id} className="p-3 rounded-lg border border-border/50 hover:bg-primary/5 transition-colors">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium text-sm">{gap.concept}</span>
                                  <Badge
                                    variant="outline"
                                    className={
                                      gap.severity === "high"
                                        ? "text-red-400 border-red-400/30"
                                        : gap.severity === "medium"
                                        ? "text-orange-400 border-orange-400/30"
                                        : "text-yellow-400 border-yellow-400/30"
                                    }
                                  >
                                    {gap.severity}
                                  </Badge>
                                </div>
                                <p className="text-xs text-muted-foreground">{gap.recommendation}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="h-full flex items-center justify-center">
                            <div className="text-center">
                              <CheckCircle2 className="w-8 h-8 text-green-400/50 mx-auto mb-2" />
                              <p className="text-sm text-muted-foreground">No gaps identified yet</p>
                            </div>
                          </div>
                        )}
                      </ScrollArea>
                    </CardContent>
                  </Card>

                  {/* Recent Activity */}
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-blue-400" />
                        Recent Topics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-[200px]">
                        {recentTopics.length > 0 ? (
                          <div className="space-y-3">
                            {recentTopics.map((topic) => (
                              <TopicCard key={topic.id} topic={topic} onSelect={() => navigate(`/learn?topic=${topic.id}`)} />
                            ))}
                          </div>
                        ) : (
                          <div className="h-full flex items-center justify-center">
                            <div className="text-center">
                              <BookOpen className="w-8 h-8 text-muted-foreground/50 mx-auto mb-2" />
                              <p className="text-sm text-muted-foreground">No recent activity</p>
                            </div>
                          </div>
                        )}
                      </ScrollArea>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

            {/* Progress Tab */}
            <TabsContent value="progress" className="space-y-6">
              {!hasData ? (
                <Card className="glass-card">
                  <CardContent className="py-12">
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center mx-auto">
                        <TrendingUp className="w-8 h-8 text-primary" />
                      </div>
                      <h3 className="text-xl font-semibold">Track Your Progress</h3>
                      <p className="text-muted-foreground max-w-md mx-auto">
                        Complete learning sessions to see detailed analytics about your question performance and time investment.
                      </p>
                      <Button onClick={() => navigate("/learn")} className="gap-2">
                        <Play className="w-4 h-4" />
                        Start Learning
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <>
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* Questions Answered Chart */}
                    <Card className="glass-card">
                      <CardHeader>
                        <CardTitle>Questions Answered</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {chartPerformanceHistory && chartPerformanceHistory.length > 0 ? (
                          <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartPerformanceHistory}>
                              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 15% 25%)" />
                              <XAxis
                                dataKey="date"
                                stroke="hsl(215 20.2% 65.1%)"
                                fontSize={12}
                                tickFormatter={(value) => new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                              />
                              <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: "hsl(220 20% 12%)",
                                  border: "1px solid hsl(220 15% 25%)",
                                  borderRadius: "8px",
                                }}
                              />
                              <Legend />
                              <Bar dataKey="correctAnswers" name="Correct" fill="hsl(142 71% 45%)" radius={[4, 4, 0, 0]} />
                              <Bar dataKey="questionsAttempted" name="Attempted" fill="hsl(263 70% 62%)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        ) : (
                          <div className="h-[300px] flex items-center justify-center">
                            <p className="text-muted-foreground">Complete sessions to see your question performance</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Time Spent Chart */}
                    <Card className="glass-card">
                      <CardHeader>
                        <CardTitle>Time Invested</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {chartPerformanceHistory && chartPerformanceHistory.length > 0 ? (
                          <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={chartPerformanceHistory}>
                              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 15% 25%)" />
                              <XAxis
                                dataKey="date"
                                stroke="hsl(215 20.2% 65.1%)"
                                fontSize={12}
                                tickFormatter={(value) => new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                              />
                              <YAxis stroke="hsl(215 20.2% 65.1%)" fontSize={12} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: "hsl(220 20% 12%)",
                                  border: "1px solid hsl(220 15% 25%)",
                                  borderRadius: "8px",
                                }}
                              />
                              <Line type="monotone" dataKey="timeSpent" name="Minutes" stroke="hsl(189 94% 43%)" strokeWidth={2} dot={{ fill: "hsl(189 94% 43%)" }} />
                            </LineChart>
                          </ResponsiveContainer>
                        ) : (
                          <div className="h-[300px] flex items-center justify-center">
                            <p className="text-muted-foreground">Complete sessions to track time invested</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>

                  {/* Concept Mastery Details */}
                  <Card className="glass-card">
                    <CardHeader>
                      <CardTitle>Concept Mastery Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {conceptMastery && conceptMastery.length > 0 ? (
                        <div className="space-y-4">
                          {conceptMastery.map((concept) => (
                            <div key={concept.concept} className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="font-medium">{concept.concept}</span>
                                <div className="flex items-center gap-2">
                                  <Badge
                                    variant="outline"
                                    className={
                                      concept.trend === "improving"
                                        ? "text-green-400 border-green-400/30"
                                        : concept.trend === "declining"
                                        ? "text-red-400 border-red-400/30"
                                        : "text-muted-foreground"
                                    }
                                  >
                                    {concept.trend === "improving" && "↑"}
                                    {concept.trend === "declining" && "↓"}
                                    {concept.trend === "stable" && "→"} {concept.trend}
                                  </Badge>
                                  <span className="text-sm font-semibold">{concept.mastery}%</span>
                                </div>
                              </div>
                              <Progress value={concept.mastery} className="h-2" />
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="py-8 text-center">
                          <p className="text-muted-foreground">Complete sessions to see concept mastery analysis</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </>
              )}
            </TabsContent>

            {/* Topics Tab */}
            <TabsContent value="topics" className="space-y-6">
              {recentTopics.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recentTopics.map((topic) => (
                    <Card key={topic.id} className="glass-card hover:scale-105 transition-all duration-300 cursor-pointer" onClick={() => navigate(`/learn?topic=${topic.id}`)}>
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <Badge variant="secondary">{topic.subject}</Badge>
                          <Badge
                            variant="outline"
                            className={topic.status === "completed" ? "text-green-400 border-green-400/30" : "text-yellow-400 border-yellow-400/30"}
                          >
                            {topic.status}
                          </Badge>
                        </div>
                        <CardTitle className="text-lg">{topic.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Progress</span>
                            <span className="font-medium">{topic.progress}%</span>
                          </div>
                          <Progress value={topic.progress} className="h-2" />
                          {topic.score && (
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-muted-foreground">Score</span>
                              <span className="font-medium gradient-text">{topic.score}%</span>
                            </div>
                          )}
                        <Button className="w-full mt-2 gap-2">
                          <Play className="w-4 h-4" />
                          {topic.status === "completed" ? "Review" : "Continue"}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              ) : (
                <Card className="glass-card">
                  <CardContent className="py-12">
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center mx-auto">
                        <BookOpen className="w-8 h-8 text-primary" />
                      </div>
                      <h3 className="text-xl font-semibold">Explore Topics</h3>
                      <p className="text-muted-foreground max-w-md mx-auto">
                        Start a learning session to build your topic library. Your studied topics will appear here.
                      </p>
                      <Button onClick={() => navigate("/learn")} className="gap-2">
                        <Play className="w-4 h-4" />
                        Start Learning
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Insights Tab */}
            <TabsContent value="insights" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-400" />
                      Learning Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {stats.questionsAnswered > 0 && (
                      <InsightCard 
                        title="Questions Completed" 
                        description={`You've answered ${stats.questionsAnswered} questions with ${Math.round((stats.correctAnswers / stats.questionsAnswered) * 100) || 0}% accuracy`} 
                        icon={CheckCircle2} 
                        color="text-green-400" 
                      />
                    )}
                    {learnerProfile?.weaknesses?.length > 0 && (
                      <InsightCard 
                        title="Areas to Improve" 
                        description={`Focus on: ${learnerProfile.weaknesses.slice(0, 2).join(', ')}`} 
                        icon={AlertTriangle} 
                        color="text-orange-400" 
                      />
                    )}
                    {learnerProfile?.strengths?.length > 0 && (
                      <InsightCard 
                        title="Your Strengths" 
                        description={`Strong in: ${learnerProfile.strengths.slice(0, 2).join(', ')}`} 
                        icon={Target} 
                        color="text-blue-400" 
                      />
                    )}
                    {stats.streakDays > 0 && (
                      <InsightCard 
                        title="Learning Streak" 
                        description={`${stats.streakDays} day streak! Keep it up!`} 
                        icon={Flame} 
                        color="text-red-400" 
                      />
                    )}
                    {stats.totalTimeSpent > 0 && (
                      <InsightCard 
                        title="Study Time" 
                        description={`You've studied for ${Math.floor(stats.totalTimeSpent / 60)} hours ${stats.totalTimeSpent % 60} minutes`} 
                        icon={Clock} 
                        color="text-purple-400" 
                      />
                    )}
                    {stats.questionsAnswered === 0 && (
                      <InsightCard 
                        title="Get Started" 
                        description="Complete some learning sessions to see your insights here!" 
                        icon={BookOpen} 
                        color="text-primary" 
                      />
                    )}
                  </CardContent>
                </Card>

                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-green-400" />
                      Your Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <GoalCard 
                      title="Sessions Completed" 
                      progress={Math.min(stats.completedSessions * 10, 100)} 
                      current={stats.completedSessions} 
                      target={10} 
                    />
                    <GoalCard 
                      title="Questions Answered" 
                      progress={Math.min(stats.questionsAnswered, 100)} 
                      current={stats.questionsAnswered} 
                      target={100} 
                    />
                    {learnerProfile?.overall_mastery > 0 && (
                      <GoalCard 
                        title="Overall Mastery" 
                        progress={learnerProfile.overall_mastery} 
                        current={Math.round(learnerProfile.overall_mastery)} 
                        target={100} 
                        unit="%" 
                      />
                    )}
                    {stats.questionsAnswered > 0 && (
                      <GoalCard 
                        title="Accuracy Rate" 
                        progress={Math.round((stats.correctAnswers / stats.questionsAnswered) * 100) || 0} 
                        current={Math.round((stats.correctAnswers / stats.questionsAnswered) * 100) || 0} 
                        target={100} 
                        unit="%" 
                      />
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
};

// Sub-components
const StatCard = ({ icon: Icon, label, value, color }) => (
  <div className="glass-card p-4 rounded-xl text-center">
    <Icon className={`w-5 h-5 mx-auto mb-2 ${color}`} />
    <div className="text-xl font-bold">{value}</div>
    <div className="text-xs text-muted-foreground">{label}</div>
  </div>
);

const TopicCard = ({ topic, onSelect }) => (
  <div className="flex items-center gap-3 p-3 rounded-lg border border-border/50 hover:bg-primary/5 transition-colors cursor-pointer" onClick={onSelect}>
    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
      <BookOpen className="w-5 h-5 text-primary" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-sm truncate">{topic.name}</p>
      <p className="text-xs text-muted-foreground">{topic.subject || "General"}</p>
    </div>
    <Badge variant="outline" className="text-xs">
      {topic.status || "study"}
    </Badge>
  </div>
);

const InsightCard = ({ title, description, icon: Icon, color }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-primary/5 border border-primary/10">
    <div className={`w-8 h-8 rounded-lg bg-background flex items-center justify-center ${color}`}>
      <Icon className="w-4 h-4" />
    </div>
    <div>
      <p className="font-medium text-sm">{title}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  </div>
);

const GoalCard = ({ title, progress, current, target, unit = "" }) => (
  <div className="space-y-2">
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium">{title}</span>
      <span className="text-sm text-muted-foreground">
        {current}
        {unit} / {target}
        {unit}
      </span>
    </div>
    <Progress value={progress} className="h-2" />
  </div>
);

export default DashboardPage;
