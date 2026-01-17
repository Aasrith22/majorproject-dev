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
import { SessionSummary } from "@/components/learning/SessionSummary";
import {
  BookOpen,
  Play,
  StopCircle,
  RefreshCw,
  ChevronLeft,
  Clock,
  Loader2,
  ListChecks,
  TextCursorInput,
  FileText,
  Brain,
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
            <div className="max-w-lg mx-auto">
              <Card className="glass-card p-6">
                <div className="text-center mb-6">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mx-auto mb-3">
                    <BookOpen className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h2 className="text-xl font-bold mb-1">Start Learning</h2>
                  <p className="text-sm text-muted-foreground">
                    Configure your session below
                  </p>
                </div>

                <div className="space-y-4">
                  {/* Test Type Selection */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Question Type</label>
                    <Select value={selectedTestType} onValueChange={setSelectedTestType}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose format..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mcq">
                          <div className="flex items-center gap-2">
                            <ListChecks className="w-4 h-4 text-blue-400" />
                            Multiple Choice
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
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Topic</label>
                    <div className="flex gap-1 p-1 rounded-lg bg-muted/50">
                      <Button
                        type="button"
                        variant={!isCustomTopic ? "secondary" : "ghost"}
                        size="sm"
                        className="flex-1 gap-1.5"
                        onClick={() => setIsCustomTopic(false)}
                      >
                        <BookOpen className="w-3.5 h-3.5" />
                        Course
                      </Button>
                      <Button
                        type="button"
                        variant={isCustomTopic ? "secondary" : "ghost"}
                        size="sm"
                        className="flex-1 gap-1.5"
                        onClick={() => setIsCustomTopic(true)}
                      >
                        <Brain className="w-3.5 h-3.5" />
                        Custom
                      </Button>
                    </div>
                  </div>

                  {/* Topic Selection or Custom Input */}
                  {!isCustomTopic ? (
                    <Select value={selectedTopicId} onValueChange={setSelectedTopicId} disabled={isLoadingTopics}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a course..." />
                      </SelectTrigger>
                      <SelectContent>
                        {topics.map((topic) => (
                          <SelectItem key={topic.id} value={topic.id}>
                            {topic.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      value={customTopic}
                      onChange={(e) => setCustomTopic(e.target.value)}
                      placeholder="Enter any topic or question..."
                    />
                  )}

                  {/* Number of Questions Selection */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Questions</label>
                    <Select value={questionCount.toString()} onValueChange={(value) => setQuestionCount(parseInt(value))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="3">3 Questions</SelectItem>
                        <SelectItem value="5">5 Questions</SelectItem>
                        <SelectItem value="10">10 Questions</SelectItem>
                        <SelectItem value="15">15 Questions</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Start Button */}
                  <Button 
                    onClick={handleStartSession} 
                    disabled={isCustomTopic ? !customTopic.trim() : (!selectedTopicId || isLoadingTopics)} 
                    className="w-full gap-2 mt-2" 
                  >
                    <Play className="w-4 h-4" />
                    Start Session
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
                      <Button onClick={() => generateQuestion(null, selectedTestType)}>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Generate Question
                      </Button>
                    </div>
                  </Card>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Session Info - Simplified */}
                <Card className="glass-card p-4">
                  <h4 className="font-semibold mb-4 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    Session Info
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Topic</span>
                      <span className="text-sm font-medium truncate max-w-[150px]" title={isCustomTopic ? customTopic : selectedTopic?.name}>
                        {isCustomTopic ? customTopic : selectedTopic?.name}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Time</span>
                      <span className="text-sm font-mono">{formatTime(sessionTime)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Progress</span>
                      <span className="text-sm font-medium">
                        {state.currentQuestionNumber}/{state.totalQuestions}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Correct</span>
                      <span className="text-sm font-medium text-green-400">
                        {state.allFeedback?.filter(f => f.isCorrect).length || 0}
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
