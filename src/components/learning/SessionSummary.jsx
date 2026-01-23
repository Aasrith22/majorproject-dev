import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  CheckCircle2,
  XCircle,
  Trophy,
  Clock,
  Home,
  RotateCcw,
  Star,
  BarChart3,
  ChevronDown,
  FileText,
  ListChecks,
  TextCursorInput,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Display session summary after completing a learning session
 * Simplified version - detailed analytics are in the dashboard
 */
export const SessionSummary = ({
  feedback,
  totalQuestions,
  sessionTime,
  onStartNewSession,
  onGoHome,
}) => {
  // Calculate overall statistics
  const correctAnswers = feedback.filter((f) => f.isCorrect).length;
  const averageScore = feedback.length > 0
    ? Math.round(feedback.reduce((sum, f) => sum + f.score, 0) / feedback.length)
    : 0;
  const accuracy = Math.round((correctAnswers / totalQuestions) * 100);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getPerformanceMessage = () => {
    if (accuracy >= 90) return { text: "Outstanding!", color: "text-green-400" };
    if (accuracy >= 70) return { text: "Great Job!", color: "text-blue-400" };
    if (accuracy >= 50) return { text: "Good Effort!", color: "text-yellow-400" };
    return { text: "Keep Practicing!", color: "text-orange-400" };
  };

  const performance = getPerformanceMessage();

  // Render star rating based on accuracy
  const renderStars = () => {
    const stars = accuracy >= 90 ? 5 : accuracy >= 70 ? 4 : accuracy >= 50 ? 3 : accuracy >= 30 ? 2 : 1;
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={cn(
              "w-4 h-4",
              star <= stars ? "text-yellow-400 fill-yellow-400" : "text-muted-foreground/30"
            )}
          />
        ))}
      </div>
    );
  };

  return (
    <Card className="glass-card overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-border/50 bg-gradient-to-r from-primary/10 via-accent/10 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Trophy className="w-8 h-8 text-primary-foreground" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Session Complete!</h2>
              <p className={cn("text-lg font-semibold", performance.color)}>
                {performance.text}
              </p>
              {renderStars()}
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold gradient-text">
              {averageScore}%
            </div>
            <p className="text-sm text-muted-foreground">Average Score</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span className="text-sm text-muted-foreground">Correct</span>
              </div>
              <p className="text-2xl font-bold text-green-400">
                {correctAnswers}/{totalQuestions}
              </p>
            </div>
            <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/20">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-orange-400" />
                <span className="text-sm text-muted-foreground">Duration</span>
              </div>
              <p className="text-2xl font-bold text-orange-400">{formatTime(sessionTime)}</p>
            </div>
          </div>

          {/* Question-by-Question Results */}
          <div className="space-y-3">
            <h4 className="font-semibold flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              Question Results
            </h4>
            <Accordion type="multiple" className="space-y-2">
              {feedback.map((f, index) => (
                <AccordionItem
                  key={f.id}
                  value={`question-${index}`}
                  className={cn(
                    "border rounded-lg overflow-hidden",
                    f.isCorrect
                      ? "bg-green-500/5 border-green-500/20"
                      : "bg-orange-500/5 border-orange-500/20"
                  )}
                >
                  <AccordionTrigger className="px-3 py-2 hover:no-underline">
                    <div className="flex items-center justify-between w-full pr-2">
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold",
                            f.isCorrect ? "bg-green-500/20 text-green-400" : "bg-orange-500/20 text-orange-400"
                          )}
                        >
                          {index + 1}
                        </div>
                        <div className="flex items-center gap-2">
                          {f.isCorrect ? (
                            <CheckCircle2 className="w-4 h-4 text-green-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-orange-400" />
                          )}
                          <span className="text-sm">
                            Question {index + 1}
                          </span>
                          {f.questionDetails?.type && (
                            <Badge variant="outline" className="text-xs ml-1">
                              {f.questionDetails.type === 'multiple-choice' && <ListChecks className="w-3 h-3 mr-1" />}
                              {f.questionDetails.type === 'fill-in-blank' && <TextCursorInput className="w-3 h-3 mr-1" />}
                              {f.questionDetails.type === 'essay' && <FileText className="w-3 h-3 mr-1" />}
                              {f.questionDetails.type === 'multiple-choice' ? 'MCQ' : 
                               f.questionDetails.type === 'fill-in-blank' ? 'Fill' : 
                               f.questionDetails.type === 'essay' ? 'Essay' : f.questionDetails.type}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Progress value={f.score} className="w-20 h-2" />
                        <Badge variant={f.isCorrect ? "default" : "secondary"}>
                          {f.score}%
                        </Badge>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-3 pb-3">
                    <div className="space-y-3 pt-2 border-t border-border/30">
                      {/* Question Text */}
                      {f.questionDetails?.content && (
                        <div className="space-y-1">
                          <p className="text-xs font-medium text-muted-foreground">Question:</p>
                          <p className="text-sm">{f.questionDetails.content}</p>
                        </div>
                      )}
                      
                      {/* Answer Details based on question type */}
                      {f.questionDetails?.type === 'multiple-choice' && (
                        <div className="space-y-3">
                          {/* Your Answer vs Correct Answer Summary */}
                          <div className="grid grid-cols-2 gap-3">
                            <div className={cn(
                              "p-2 rounded border",
                              f.isCorrect 
                                ? "bg-green-500/10 border-green-500/30" 
                                : "bg-red-500/10 border-red-500/30"
                            )}>
                              <p className="text-xs font-medium text-muted-foreground mb-1">Your Answer:</p>
                              <p className={cn(
                                "text-sm font-medium",
                                f.isCorrect ? "text-green-400" : "text-red-400"
                              )}>
                                {f.questionDetails.options?.find(opt => 
                                  opt.id === f.userSelectedOptionId || opt.text === f.userAnswer
                                )?.text || f.userAnswer || "No answer"}
                              </p>
                            </div>
                            <div className="p-2 rounded bg-green-500/10 border border-green-500/30">
                              <p className="text-xs font-medium text-muted-foreground mb-1">Correct Answer:</p>
                              <p className="text-sm font-medium text-green-400">
                                {(() => {
                                  const correctAns = f.correctAnswer || f.questionDetails.correctAnswer;
                                  const matchedOption = f.questionDetails.options?.find(opt => 
                                    opt.id === correctAns || opt.text === correctAns
                                  );
                                  return matchedOption?.text || correctAns || "N/A";
                                })()}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {f.questionDetails?.type === 'fill-in-blank' && (
                        <div className="space-y-2">
                          <div className="grid grid-cols-2 gap-3">
                            <div className={cn(
                              "p-2 rounded border",
                              f.isCorrect 
                                ? "bg-green-500/10 border-green-500/30" 
                                : "bg-red-500/10 border-red-500/30"
                            )}>
                              <p className="text-xs font-medium text-muted-foreground mb-1">Your Answer:</p>
                              <p className={cn(
                                "text-sm font-medium",
                                f.isCorrect ? "text-green-400" : "text-red-400"
                              )}>
                                {f.userAnswer || "No answer"}
                              </p>
                            </div>
                            <div className="p-2 rounded bg-green-500/10 border border-green-500/30">
                              <p className="text-xs font-medium text-muted-foreground mb-1">Correct Answer:</p>
                              <p className="text-sm font-medium text-green-400">
                                {f.correctAnswer || f.questionDetails.correctAnswer || "N/A"}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {f.questionDetails?.type === 'essay' && (
                        <div className="space-y-3">
                          <div className="p-3 rounded bg-muted/30">
                            <p className="text-xs font-medium text-muted-foreground mb-1">Your Answer:</p>
                            <p className="text-sm whitespace-pre-wrap">
                              {f.userAnswer || "No answer provided"}
                            </p>
                          </div>
                          <div className="flex items-center gap-4 p-3 rounded bg-primary/5 border border-primary/20">
                            <div className="flex-1">
                              <p className="text-xs font-medium text-muted-foreground mb-1">Essay Score:</p>
                              <div className="flex items-center gap-2">
                                <Progress value={f.score} className="flex-1 h-3" />
                                <span className={cn(
                                  "text-lg font-bold",
                                  f.score >= 70 ? "text-green-400" : f.score >= 50 ? "text-yellow-400" : "text-orange-400"
                                )}>
                                  {f.score}%
                                </span>
                              </div>
                            </div>
                          </div>
                          {f.explanation && (
                            <div className="p-3 rounded bg-blue-500/5 border border-blue-500/20">
                              <p className="text-xs font-medium text-blue-400 mb-1">Feedback:</p>
                              <p className="text-sm text-muted-foreground">{f.explanation}</p>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Explanation for non-essay questions */}
                      {f.explanation && f.questionDetails?.type !== 'essay' && (
                        <div className="p-2 rounded bg-blue-500/5 border border-blue-500/20">
                          <p className="text-xs font-medium text-blue-400 mb-1">Explanation:</p>
                          <p className="text-sm text-muted-foreground">{f.explanation}</p>
                        </div>
                      )}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>

          {/* Dashboard Link */}
          <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 text-center">
            <p className="text-sm text-muted-foreground mb-2">
              View detailed analytics and track your progress
            </p>
            <Button variant="outline" onClick={onGoHome} className="gap-2">
              <BarChart3 className="w-4 h-4" />
              Go to Dashboard
            </Button>
          </div>
      </div>

      {/* Action Footer */}
      <div className="p-4 border-t border-border/50 bg-background/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className={cn("w-5 h-5", performance.color)} />
            <span className="text-sm text-muted-foreground">
              {correctAnswers} out of {totalQuestions} correct
            </span>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onGoHome} className="gap-2">
              <Home className="w-4 h-4" />
              Go Home
            </Button>
            <Button onClick={onStartNewSession} className="gap-2">
              <RotateCcw className="w-4 h-4" />
              New Session
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};
