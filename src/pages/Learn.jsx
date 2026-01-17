import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { useLearning } from "@/context/LearningContext";
import { MultimodalInput } from "@/components/learning/MultimodalInput";
import { QuestionDisplay } from "@/components/learning/QuestionDisplay";
import { AgentStatus } from "@/components/learning/AgentStatus";
import { SessionSummary } from "@/components/learning/SessionSummary";
import {
  BookOpen,
  Play,
  StopCircle,
  RefreshCw,
  ChevronLeft,
  Clock,
  Target,
  Zap,
  Loader2,
  ListChecks,
  TextCursorInput,
  FileText,
  Hash,
  Brain,
  TrendingUp,
} from "lucide-react";
import apiService from "@/services/unified-api.service.js";

export const LearnPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const topicIdParam = searchParams.get("topic");

  const {
    state,
    loadUserProfile,
    startLearningSession,
    endLearningSession,
    generateQuestion,
    submitAnswer,
  } = useLearning();

  const [topics, setTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState(topicIdParam || "");
  const [customTopic, setCustomTopic] = useState("");
  const [isCustomTopic, setIsCustomTopic] = useState(false);
  const [selectedTestType, setSelectedTestType] = useState("mcq");
  const [questionCount, setQuestionCount] = useState(5);
  const [sessionTime, setSessionTime] = useState(0);
  const [isLoadingTopics, setIsLoadingTopics] = useState(true);

  // Load topics on mount
  useEffect(() => {
    const loadTopics = async () => {
      setIsLoadingTopics(true);
      try {
        const topicsData = await apiService.getTopics();
        setTopics(topicsData);
        
        // Check if URL param is a topic name (from Index page navigation)
        if (topicIdParam) {
          const decodedTopic = decodeURIComponent(topicIdParam);
          // Check if it matches a known topic name
          const matchingTopic = topicsData.find(t => 
            t.name === decodedTopic || 
            t.id === decodedTopic ||
            t.name.toLowerCase() === decodedTopic.toLowerCase()
          );
          
          if (matchingTopic) {
            // It's a predefined topic
            setSelectedTopicId(matchingTopic.id);
            setIsCustomTopic(false);
          } else {
            // It's a custom topic from URL
            setCustomTopic(decodedTopic);
            setIsCustomTopic(true);
            setSelectedTopicId("");
          }
        } else if (!selectedTopicId && topicsData.length > 0) {
          setSelectedTopicId(topicsData[0].id);
        }
      } catch (error) {
        console.error("Failed to load topics:", error);
      } finally {
        setIsLoadingTopics(false);
      }
    };

    loadTopics();
    loadUserProfile();
  }, [loadUserProfile, topicIdParam]);

  // Session timer
  useEffect(() => {
    let interval;
    if (state.isSessionActive) {
      interval = setInterval(() => {
        setSessionTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [state.isSessionActive]);

  // Auto-generate next question when current question is cleared
  useEffect(() => {
    if (
      state.isSessionActive &&
      !state.currentQuestion &&
      !state.isGeneratingQuestion &&
      !state.isLoadingQuestions &&
      !state.isSessionComplete &&
      state.currentQuestionNumber < state.totalQuestions &&
      state.sessionQuestions.length > 0
    ) {
      const timer = setTimeout(() => {
        generateQuestion(null, selectedTestType); // difficulty is null - will be random
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [
    state.isSessionActive,
    state.currentQuestion,
    state.isGeneratingQuestion,
    state.isSessionComplete,
    state.currentQuestionNumber,
    state.totalQuestions,
    generateQuestion,
    selectedTestType,
  ]);

  const handleStartSession = async () => {
    let topicToUse;
    if (isCustomTopic) {
      topicToUse = customTopic;
    } else {
      // For predefined topics, use the full topic name instead of ID
      const selectedTopic = topics.find(t => t.id === selectedTopicId);
      topicToUse = selectedTopic ? selectedTopic.name : selectedTopicId;
    }
    
    if (topicToUse) {
      // Pass the test type to the session so questions use the correct format
      await startLearningSession(topicToUse, questionCount, isCustomTopic, selectedTestType);
      setSessionTime(0);
      setTimeout(() => generateQuestion(null, selectedTestType), 500); // difficulty is null - will be random
    }
  };

  const handleEndSession = async () => {
    await endLearningSession();
    setSessionTime(0);
  };

  const handleStartNewSession = () => {
    endLearningSession();
    setSessionTime(0);
  };

  const handleSubmitAnswer = async (content, modality, selectedOptionId) => {
    await submitAnswer(content, modality, selectedOptionId);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const selectedTopic = topics.find((t) => t.id === selectedTopicId);

  return (
    <AppLayout showFooter={false}>
      <div className="min-h-screen bg-gradient-to-b from-background to-background/95">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
                <ChevronLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Learning Session</h1>
                <p className="text-muted-foreground">
                  Adaptive testing and feedback
                </p>
              </div>
            </div>

            {state.isSessionActive && (
              <div className="flex items-center gap-4">
                <Badge variant="secondary" className="gap-2 text-lg px-4 py-2">
                  <Clock className="w-4 h-4" />
                  {formatTime(sessionTime)}
                </Badge>
                <Button variant="destructive" onClick={handleEndSession} className="gap-2">
                  <StopCircle className="w-4 h-4" />
                  End Session
                </Button>
              </div>
            )}
          </div>

          {/* Main Content */}
          {!state.isSessionActive ? (
            // Session Setup
            <div className="max-w-2xl mx-auto">
              <Card className="glass-card p-8">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mx-auto mb-4">
                    <BookOpen className="w-8 h-8 text-primary-foreground" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2">Start a Learning Session</h2>
                  <p className="text-muted-foreground">
                    Choose a topic or enter a custom query to begin adaptive testing
                  </p>
                </div>

                <div className="space-y-6">
                  {/* Test Type Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Question Type</label>
                    <Select value={selectedTestType} onValueChange={setSelectedTestType}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose question format..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mcq">
                          <div className="flex items-center gap-2">
                            <ListChecks className="w-4 h-4 text-blue-400" />
                            Multiple Choice Questions
                          </div>
                        </SelectItem>
                        <SelectItem value="fill-in-blank">
                          <div className="flex items-center gap-2">
                            <TextCursorInput className="w-4 h-4 text-purple-400" />
                            Fill in the Blanks
                          </div>
                        </SelectItem>
                        <SelectItem value="essay">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-green-400" />
                            Essay Answers
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Topic Selection Mode Toggle */}
                  <div className="space-y-3">
                    <label className="text-sm font-medium">Topic</label>
                    <div className="flex gap-2 p-1 rounded-lg bg-muted/50">
                      <Button
                        type="button"
                        variant={!isCustomTopic ? "secondary" : "ghost"}
                        className="flex-1 gap-2"
                        onClick={() => setIsCustomTopic(false)}
                      >
                        <BookOpen className="w-4 h-4" />
                        Select Course
                      </Button>
                      <Button
                        type="button"
                        variant={isCustomTopic ? "secondary" : "ghost"}
                        className="flex-1 gap-2"
                        onClick={() => setIsCustomTopic(true)}
                      >
                        <Brain className="w-4 h-4" />
                        Custom Query
                      </Button>
                    </div>
                  </div>

                  {/* Topic Selection or Custom Input */}
                  {!isCustomTopic ? (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Select from Courses</label>
                      <Select value={selectedTopicId} onValueChange={setSelectedTopicId} disabled={isLoadingTopics}>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Choose a topic..." />
                        </SelectTrigger>
                        <SelectContent>
                          {topics.map((topic) => (
                            <SelectItem key={topic.id} value={topic.id}>
                              <div className="flex items-center gap-2">
                                <span>{topic.name}</span>
                                <Badge variant={topic.isCustom ? "secondary" : "outline"} className="text-xs">
                                  {topic.isCustom ? "Custom" : topic.subject}
                                </Badge>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Enter Topic or Query</label>
                      <Input
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                        placeholder="e.g., Binary Search Trees, Machine Learning basics, Explain recursion..."
                        className="w-full"
                      />
                      <p className="text-xs text-muted-foreground">
                        Type any topic, concept, or question. Our AI will generate relevant questions.
                      </p>
                    </div>
                  )}

                  {/* Number of Questions Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Number of Questions</label>
                    <Select value={questionCount.toString()} onValueChange={(value) => setQuestionCount(parseInt(value))}>
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="3">
                          <div className="flex items-center gap-2">
                            <Hash className="w-4 h-4 text-blue-400" />
                            3 Questions - Quick Test
                          </div>
                        </SelectItem>
                        <SelectItem value="5">
                          <div className="flex items-center gap-2">
                            <Hash className="w-4 h-4 text-green-400" />
                            5 Questions - Standard
                          </div>
                        </SelectItem>
                        <SelectItem value="10">
                          <div className="flex items-center gap-2">
                            <Hash className="w-4 h-4 text-yellow-400" />
                            10 Questions - Comprehensive
                          </div>
                        </SelectItem>
                        <SelectItem value="15">
                          <div className="flex items-center gap-2">
                            <Hash className="w-4 h-4 text-orange-400" />
                            15 Questions - Full Assessment
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Topic Preview */}
                  {!isCustomTopic && selectedTopic && (
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{selectedTopic.name}</h4>
                        <Badge variant="secondary">{selectedTopic.subject}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {selectedTopic.description || `Continue learning ${selectedTopic.name} in ${selectedTopic.subject}`}
                      </p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="flex items-center gap-1">
                          <Zap className="w-4 h-4 text-primary" />
                          {selectedTopic.progress}% complete
                        </span>
                        {selectedTopic.score && (
                          <span className="flex items-center gap-1">
                            <Target className="w-4 h-4 text-secondary" />
                            {selectedTopic.score}% score
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Custom Topic Preview */}
                  {isCustomTopic && customTopic && (
                    <div className="p-4 rounded-lg bg-secondary/5 border border-secondary/20">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-5 h-5 text-secondary" />
                        <h4 className="font-semibold">Custom Query</h4>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        "{customTopic}"
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        AI will analyze your query and generate adaptive questions
                      </p>
                    </div>
                  )}

                  {/* Start Button */}
                  <Button 
                    onClick={handleStartSession} 
                    disabled={isCustomTopic ? !customTopic.trim() : (!selectedTopicId || isLoadingTopics)} 
                    className="w-full gap-2" 
                    size="lg"
                  >
                    <Play className="w-5 h-5" />
                    Start Learning Session
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            // Active Session
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Main Content Area */}
              <div className="lg:col-span-2 space-y-6">
                {/* Session Complete - Show Summary */}
                {state.isSessionComplete ? (
                  <SessionSummary
                    feedback={state.allFeedback}
                    totalQuestions={state.totalQuestions}
                    sessionTime={sessionTime}
                    onStartNewSession={handleStartNewSession}
                    onGoHome={() => navigate("/")}
                    sessionAnalytics={state.sessionAnalytics}
                  />
                ) : state.isGeneratingQuestion ? (
                  <Card className="glass-card p-12">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <Loader2 className="w-12 h-12 text-primary animate-spin" />
                      <p className="text-lg font-medium">
                        Generating question {state.currentQuestionNumber + 1} of {state.totalQuestions}...
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Our AI agents are working to create the perfect challenge
                      </p>
                    </div>
                  </Card>
                ) : state.isSubmittingAnswer ? (
                  <Card className="glass-card p-12">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <Loader2 className="w-12 h-12 text-primary animate-spin" />
                      <p className="text-lg font-medium">Evaluating your answer...</p>
                      <p className="text-sm text-muted-foreground">
                        Processing question {state.currentQuestionNumber} of {state.totalQuestions}
                      </p>
                    </div>
                  </Card>
                ) : state.currentQuestion ? (
                  <>
                    {/* Progress indicator */}
                    <Card className="glass-card p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">
                          Question {state.currentQuestionNumber} of {state.totalQuestions}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {Math.round((state.currentQuestionNumber / state.totalQuestions) * 100)}% complete
                        </span>
                      </div>
                      <Progress value={(state.currentQuestionNumber / state.totalQuestions) * 100} className="h-2" />
                    </Card>
                    <QuestionDisplay
                      question={state.currentQuestion}
                      onSubmit={handleSubmitAnswer}
                      isSubmitting={state.isSubmittingAnswer}
                    />
                    {/* Only show MultimodalInput for non-MCQ questions */}
                    {state.currentQuestion.type !== "multiple-choice" && (
                      <MultimodalInput
                        onSubmit={handleSubmitAnswer}
                        isLoading={state.isSubmittingAnswer}
                        placeholder="Enter your answer..."
                        questionType={state.currentQuestion.type}
                      />
                    )}
                  </>
                ) : (
                  <Card className="glass-card p-12">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <BookOpen className="w-12 h-12 text-muted-foreground" />
                      <p className="text-lg font-medium">Ready to Learn</p>
                      <Button onClick={() => generateQuestion(selectedDifficulty, selectedTestType)}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Generate Question
                      </Button>
                    </div>
                  </Card>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Agent Status */}
                <AgentStatus agentResponses={state.agentResponses} />

                {/* Adaptive Difficulty Info */}
                {state.adaptivityState && state.adaptivityState.recentPerformance && (
                  <Card className="glass-card p-4">
                    <h4 className="font-semibold mb-4 flex items-center gap-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      Adaptive Learning
                    </h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Recent Performance</span>
                        <span className="text-sm font-medium flex items-center gap-1">
                          <TrendingUp className="w-3 h-3 text-green-400" />
                          {state.adaptivityState.recentPerformance.avgScore?.toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Correct Answers</span>
                        <span className="text-sm font-medium">
                          {state.adaptivityState.recentPerformance.correctCount}/{state.adaptivityState.recentPerformance.totalQuestions}
                        </span>
                      </div>
                    </div>
                  </Card>
                )}

                {/* Session Info */}
                <Card className="glass-card p-4">
                  <h4 className="font-semibold mb-4 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    Current Session
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Topic</span>
                      <span className="text-sm font-medium truncate max-w-[150px]" title={isCustomTopic ? customTopic : selectedTopic?.name}>
                        {isCustomTopic ? customTopic : selectedTopic?.name}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Type</span>
                      <Badge
                        variant="outline"
                        className={
                          selectedTestType === "mcq"
                            ? "text-blue-400"
                            : selectedTestType === "fill-in-blank"
                            ? "text-purple-400"
                            : "text-green-400"
                        }
                      >
                        {selectedTestType === "mcq" ? "MCQ" : selectedTestType === "fill-in-blank" ? "Fill in Blanks" : "Essay"}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Duration</span>
                      <span className="text-sm font-mono">{formatTime(sessionTime)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Progress</span>
                      <span className="text-sm font-medium">
                        {state.currentQuestionNumber}/{state.totalQuestions}
                      </span>
                    </div>
                    <div className="pt-2">
                      <Progress value={(state.currentQuestionNumber / state.totalQuestions) * 100} className="h-2" />
                    </div>
                  </div>
                </Card>

                {/* Quick Actions */}
                <Card className="glass-card p-4">
                  <h4 className="font-semibold mb-4">Quick Actions</h4>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full" onClick={() => navigate("/dashboard")}>
                      View Dashboard
                    </Button>
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default LearnPage;
