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
import { ScrollArea } from "@/components/ui/scroll-area";
import { useLearning } from "@/context/LearningContext";
import { MultimodalInput } from "@/components/learning/MultimodalInput";
import { QuestionDisplay } from "@/components/learning/QuestionDisplay";
import { FeedbackDisplay } from "@/components/learning/FeedbackDisplay";
import { AgentStatus } from "@/components/learning/AgentStatus";
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
} from "lucide-react";
import type { InputModality, Topic } from "@/types/api.types";
import apiService from "@/services/api.service";

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
    resetQuestionState,
  } = useLearning();

  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopicId, setSelectedTopicId] = useState<string>(
    topicIdParam || ""
  );
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("medium");
  const [sessionTime, setSessionTime] = useState(0);
  const [isLoadingTopics, setIsLoadingTopics] = useState(true);

  // Load topics on mount
  useEffect(() => {
    const loadTopics = async () => {
      setIsLoadingTopics(true);
      try {
        const topicsData = await apiService.getTopics();
        setTopics(topicsData);
        if (!selectedTopicId && topicsData.length > 0) {
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
  }, [loadUserProfile, selectedTopicId]);

  // Session timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (state.isSessionActive) {
      interval = setInterval(() => {
        setSessionTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [state.isSessionActive]);

  const handleStartSession = async () => {
    if (selectedTopicId) {
      await startLearningSession(selectedTopicId);
      setSessionTime(0);
      // Generate first question after session starts
      setTimeout(() => generateQuestion(selectedDifficulty), 500);
    }
  };

  const handleEndSession = async () => {
    await endLearningSession();
    setSessionTime(0);
  };

  const handleSubmitAnswer = async (
    content: string,
    modality: InputModality,
    rawData?: string
  ) => {
    await submitAnswer(content, modality);
  };

  const handleNextQuestion = () => {
    resetQuestionState();
    generateQuestion(selectedDifficulty);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const selectedTopic = topics.find((t) => t.id === selectedTopicId);

  return (
    <AppLayout showFooter={false}>
      <div className="min-h-screen bg-gradient-to-b from-background to-background/95">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate("/")}
              >
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
                <Button
                  variant="destructive"
                  onClick={handleEndSession}
                  className="gap-2"
                >
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
                  <h2 className="text-2xl font-bold mb-2">
                    Start a Learning Session
                  </h2>
                  <p className="text-muted-foreground">
                    Choose a topic and difficulty to begin adaptive testing
                  </p>
                </div>

                <div className="space-y-6">
                  {/* Topic Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Select Topic</label>
                    <Select
                      value={selectedTopicId}
                      onValueChange={setSelectedTopicId}
                      disabled={isLoadingTopics}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose a topic..." />
                      </SelectTrigger>
                      <SelectContent>
                        {topics.map((topic) => (
                          <SelectItem key={topic.id} value={topic.id}>
                            <div className="flex items-center gap-2">
                              <span>{topic.name}</span>
                              <Badge variant="outline" className="text-xs">
                                {topic.subject}
                              </Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Difficulty Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Difficulty Level</label>
                    <Select
                      value={selectedDifficulty}
                      onValueChange={setSelectedDifficulty}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="easy">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-green-400" />
                            Easy - Foundational concepts
                          </div>
                        </SelectItem>
                        <SelectItem value="medium">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-yellow-400" />
                            Medium - Applied knowledge
                          </div>
                        </SelectItem>
                        <SelectItem value="hard">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-red-400" />
                            Hard - Advanced analysis
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Topic Preview */}
                  {selectedTopic && (
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{selectedTopic.name}</h4>
                        <Badge>{selectedTopic.difficulty}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {selectedTopic.description ||
                          `Continue learning ${selectedTopic.name} in ${selectedTopic.subject}`}
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

                  {/* Start Button */}
                  <Button
                    onClick={handleStartSession}
                    disabled={!selectedTopicId || isLoadingTopics}
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
                {/* Question Display */}
                {state.isGeneratingQuestion ? (
                  <Card className="glass-card p-12">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <Loader2 className="w-12 h-12 text-primary animate-spin" />
                      <p className="text-lg font-medium">
                        Generating your next question...
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Our AI agents are working to create the perfect challenge
                      </p>
                    </div>
                  </Card>
                ) : state.currentQuestion && !state.currentFeedback ? (
                  <>
                    <QuestionDisplay question={state.currentQuestion} />
                    <MultimodalInput
                      onSubmit={handleSubmitAnswer}
                      isLoading={state.isSubmittingAnswer}
                      placeholder="Enter your answer..."
                    />
                  </>
                ) : state.currentFeedback ? (
                  <FeedbackDisplay
                    feedback={state.currentFeedback}
                    onNextQuestion={handleNextQuestion}
                  />
                ) : (
                  <Card className="glass-card p-12">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <BookOpen className="w-12 h-12 text-muted-foreground" />
                      <p className="text-lg font-medium">Ready to Learn</p>
                      <Button onClick={() => generateQuestion(selectedDifficulty)}>
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

                {/* Session Info */}
                <Card className="glass-card p-4">
                  <h4 className="font-semibold mb-4 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    Current Session
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Topic</span>
                      <span className="text-sm font-medium">
                        {selectedTopic?.name}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">
                        Difficulty
                      </span>
                      <Badge
                        variant="outline"
                        className={
                          selectedDifficulty === "easy"
                            ? "text-green-400"
                            : selectedDifficulty === "medium"
                            ? "text-yellow-400"
                            : "text-red-400"
                        }
                      >
                        {selectedDifficulty}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">
                        Duration
                      </span>
                      <span className="text-sm font-mono">
                        {formatTime(sessionTime)}
                      </span>
                    </div>
                  </div>
                </Card>

                {/* Quick Actions */}
                <Card className="glass-card p-4">
                  <h4 className="font-semibold mb-4">Quick Actions</h4>
                  <div className="space-y-2">
                    <Select
                      value={selectedDifficulty}
                      onValueChange={setSelectedDifficulty}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Change difficulty" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="easy">Easy</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="hard">Hard</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => navigate("/dashboard")}
                    >
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
