import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CheckCircle2,
  XCircle,
  Trophy,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  BarChart3,
  Home,
  RotateCcw,
  Star,
  Zap,
  AlertTriangle,
  BookOpen,
  Brain,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Display session summary after completing a learning session
 * @param {Object} props
 * @param {Array} props.feedback - Array of feedback objects from the session
 * @param {number} props.totalQuestions - Total number of questions in session
 * @param {number} props.sessionTime - Total session time in seconds
 * @param {Function} props.onStartNewSession - Callback to start new session
 * @param {Function} props.onGoHome - Callback to navigate home
 * @param {Object} props.sessionAnalytics - Enhanced analytics from feedback agent
 */
export const SessionSummary = ({
  feedback,
  totalQuestions,
  sessionTime,
  onStartNewSession,
  onGoHome,
  sessionAnalytics = {},
}) => {
  // Calculate overall statistics
  const correctAnswers = feedback.filter((f) => f.isCorrect).length;
  const averageScore = feedback.length > 0
    ? Math.round(feedback.reduce((sum, f) => sum + f.score, 0) / feedback.length)
    : 0;
  const accuracy = Math.round((correctAnswers / totalQuestions) * 100);

  // Get all unique strengths, weaknesses, and misconceptions (with null safety)
  const allStrengths = [...new Set(feedback.flatMap((f) => f.analysis?.strengths || []))];
  const allWeaknesses = [...new Set(feedback.flatMap((f) => f.analysis?.weaknesses || []))];
  const allMisconceptions = [...new Set(feedback.flatMap((f) => f.analysis?.misconceptions || []))];
  const allTargetConcepts = [...new Set(feedback.flatMap((f) => f.improvementPlan?.targetConcepts || []))];

  // Extract enhanced analytics
  const performanceRating = sessionAnalytics?.performance_rating || {};
  const difficultyAnalysis = sessionAnalytics?.difficulty_analysis || {};
  const learningMetrics = sessionAnalytics?.learning_metrics || {};
  const enhancedStrengths = sessionAnalytics?.strengths || [];
  const enhancedWeaknesses = sessionAnalytics?.weaknesses || [];
  const enhancedRecommendations = sessionAnalytics?.recommendations || [];
  const masteredConcepts = sessionAnalytics?.mastered_concepts || [];
  const improvementAreas = sessionAnalytics?.improvement_areas || [];

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getPerformanceMessage = () => {
    if (performanceRating?.rating) {
      const ratings = {
        "Excellent": { text: "Outstanding!", color: "text-green-400" },
        "Great": { text: "Great Job!", color: "text-blue-400" },
        "Good": { text: "Good Effort!", color: "text-yellow-400" },
        "Fair": { text: "Keep Practicing!", color: "text-orange-400" },
        "Needs Improvement": { text: "Room to Grow!", color: "text-orange-400" },
      };
      return ratings[performanceRating.rating] || ratings["Good"];
    }
    
    if (accuracy >= 90) return { text: "Outstanding!", color: "text-green-400" };
    if (accuracy >= 70) return { text: "Great Job!", color: "text-blue-400" };
    if (accuracy >= 50) return { text: "Good Effort!", color: "text-yellow-400" };
    return { text: "Keep Practicing!", color: "text-orange-400" };
  };

  const performance = getPerformanceMessage();

  // Render star rating
  const renderStars = (count) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={cn(
              "w-4 h-4",
              star <= count ? "text-yellow-400 fill-yellow-400" : "text-muted-foreground/30"
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
              {performanceRating?.stars && renderStars(performanceRating.stars)}
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold gradient-text">
              {performanceRating?.score ? Math.round(performanceRating.score) : averageScore}%
            </div>
            <p className="text-sm text-muted-foreground">Performance Score</p>
          </div>
        </div>
      </div>

      <ScrollArea className="max-h-[600px]">
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

          {/* Performance Breakdown - from feedback agent analytics */}
          {performanceRating?.breakdown && (
            <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 space-y-3">
              <h4 className="font-semibold flex items-center gap-2">
                <Brain className="w-4 h-4 text-primary" />
                Performance Breakdown
              </h4>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-2 rounded bg-background/50">
                  <p className="text-xs text-muted-foreground">Accuracy</p>
                  <p className="text-lg font-bold text-green-400">
                    +{performanceRating.breakdown.accuracy_contribution}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-background/50">
                  <p className="text-xs text-muted-foreground">Difficulty Bonus</p>
                  <p className="text-lg font-bold text-blue-400">
                    +{performanceRating.breakdown.difficulty_bonus}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-background/50">
                  <p className="text-xs text-muted-foreground">Consistency</p>
                  <p className="text-lg font-bold text-purple-400">
                    +{performanceRating.breakdown.consistency_bonus}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Difficulty Analysis */}
          {difficultyAnalysis?.pattern && (
            <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold flex items-center gap-2">
                  <Zap className="w-4 h-4 text-blue-400" />
                  Difficulty Analysis
                </h4>
                <Badge variant="outline" className={cn(
                  difficultyAnalysis.pattern === "increasing" ? "border-green-500 text-green-400" :
                  difficultyAnalysis.pattern === "decreasing" ? "border-orange-500 text-orange-400" :
                  "border-blue-500 text-blue-400"
                )}>
                  {difficultyAnalysis.pattern === "increasing" && <TrendingUp className="w-3 h-3 mr-1" />}
                  {difficultyAnalysis.pattern === "decreasing" && <TrendingDown className="w-3 h-3 mr-1" />}
                  {difficultyAnalysis.pattern}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{difficultyAnalysis.recommendation}</p>
            </div>
          )}

          {/* Mastered Concepts */}
          {masteredConcepts.length > 0 && (
            <div className="p-4 rounded-lg bg-green-500/5 border border-green-500/20 space-y-3">
              <h4 className="font-semibold text-green-400 flex items-center gap-2">
                <Trophy className="w-4 h-4" />
                Mastered Concepts
              </h4>
              <div className="flex flex-wrap gap-2">
                {masteredConcepts.map((concept, index) => (
                  <Badge key={index} className="bg-green-500/20 text-green-400 border-green-500/30">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    {concept}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Question-by-Question Results */}
          <div className="space-y-3">
            <h4 className="font-semibold flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-primary" />
              Question Results
            </h4>
            <div className="space-y-2">
              {feedback.map((f, index) => (
                <div
                  key={f.id}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg border",
                    f.isCorrect
                      ? "bg-green-500/5 border-green-500/20"
                      : "bg-orange-500/5 border-orange-500/20"
                  )}
                >
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
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Progress value={f.score} className="w-20 h-2" />
                    <Badge variant={f.isCorrect ? "default" : "secondary"}>
                      {f.score}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Enhanced Recommendations */}
          {enhancedRecommendations.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-primary" />
                Personalized Recommendations
              </h4>
              <div className="space-y-2">
                {enhancedRecommendations.slice(0, 3).map((rec, index) => (
                  <div
                    key={index}
                    className={cn(
                      "p-3 rounded-lg border",
                      rec.type === "review" ? "bg-orange-500/5 border-orange-500/20" :
                      rec.type === "challenge" ? "bg-green-500/5 border-green-500/20" :
                      rec.type === "explore" ? "bg-blue-500/5 border-blue-500/20" :
                      "bg-primary/5 border-primary/20"
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                        rec.priority === 1 ? "bg-red-500/20 text-red-400" :
                        rec.priority === 2 ? "bg-yellow-500/20 text-yellow-400" :
                        "bg-green-500/20 text-green-400"
                      )}>
                        {rec.priority}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{rec.title}</p>
                        <p className="text-xs text-muted-foreground mt-1">{rec.description}</p>
                        {rec.action && (
                          <p className="text-xs text-primary mt-1">→ {rec.action}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Improvement Areas */}
          {improvementAreas.length > 0 && (
            <div className="p-4 rounded-lg bg-orange-500/5 border border-orange-500/20 space-y-3">
              <h4 className="font-semibold text-orange-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Focus Areas for Next Session
              </h4>
              <div className="flex flex-wrap gap-2">
                {improvementAreas.map((area, index) => (
                  <Badge key={index} variant="outline" className="border-orange-500/30 text-orange-400">
                    {area}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-4">
            {(enhancedStrengths.length > 0 || allStrengths.length > 0) && (
              <div className="space-y-3 p-4 rounded-lg bg-green-500/5 border border-green-500/20">
                <h4 className="font-semibold text-green-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Your Strengths
                </h4>
                <ul className="space-y-2">
                  {(enhancedStrengths.length > 0 ? enhancedStrengths : allStrengths).slice(0, 4).map((strength, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-green-400 mt-1">•</span>
                      {typeof strength === 'object' ? (
                        <span>
                          {strength.concept} 
                          {strength.accuracy && <span className="text-green-400 ml-1">({strength.accuracy}%)</span>}
                        </span>
                      ) : strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(enhancedWeaknesses.length > 0 || allWeaknesses.length > 0) && (
              <div className="space-y-3 p-4 rounded-lg bg-orange-500/5 border border-orange-500/20">
                <h4 className="font-semibold text-orange-400 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Areas to Improve
                </h4>
                <ul className="space-y-2">
                  {(enhancedWeaknesses.length > 0 ? enhancedWeaknesses : allWeaknesses).slice(0, 4).map((weakness, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="text-orange-400 mt-1">•</span>
                      {typeof weakness === 'object' ? (
                        <span>
                          {weakness.concept}
                          {weakness.accuracy && <span className="text-orange-400 ml-1">({weakness.accuracy}%)</span>}
                        </span>
                      ) : weakness}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Misconceptions */}
          {allMisconceptions.length > 0 && (
            <div className="space-y-3 p-4 rounded-lg bg-destructive/10 border border-destructive/20">
              <h4 className="font-semibold text-destructive flex items-center gap-2">
                <XCircle className="w-4 h-4" />
                Misconceptions to Address
              </h4>
              <ul className="space-y-2">
                {allMisconceptions.map((misconception, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <span className="text-destructive mt-1">•</span>
                    {misconception}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Concepts to Review */}
          {allTargetConcepts.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold flex items-center gap-2">
                <Target className="w-4 h-4 text-primary" />
                Concepts to Review
              </h4>
              <div className="flex flex-wrap gap-2">
                {allTargetConcepts.map((concept, index) => (
                  <Badge key={index} variant="outline" className="cursor-pointer hover:bg-primary/10">
                    {concept}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

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
