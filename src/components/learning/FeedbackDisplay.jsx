import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Lightbulb,
  TrendingUp,
  BookOpen,
  Video,
  FileText,
  Target,
  ChevronRight,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Display feedback for a submitted answer
 * @param {Object} props
 * @param {Object} props.feedback - Feedback object from the API
 * @param {Function} props.onNextQuestion - Callback to proceed to next question
 * @param {Function} props.onReviewConcept - Callback when a concept is clicked for review
 */
export const FeedbackDisplay = ({
  feedback,
  onNextQuestion,
  onReviewConcept,
}) => {
  const getResourceIcon = (type) => {
    switch (type) {
      case "video":
        return <Video className="w-4 h-4" />;
      case "article":
        return <FileText className="w-4 h-4" />;
      case "exercise":
        return <Target className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  return (
    <Card className="glass-card overflow-hidden">
      {/* Header with Score */}
      <div
        className={cn(
          "p-6 border-b border-border/50",
          feedback.isCorrect
            ? "bg-gradient-to-r from-green-500/10 to-transparent"
            : "bg-gradient-to-r from-orange-500/10 to-transparent"
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center",
                feedback.isCorrect ? "bg-green-500/20" : "bg-orange-500/20"
              )}
            >
              {feedback.isCorrect ? (
                <CheckCircle2 className="w-6 h-6 text-green-400" />
              ) : (
                <AlertCircle className="w-6 h-6 text-orange-400" />
              )}
            </div>
            <div>
              <h3 className="text-xl font-semibold">
                {feedback.isCorrect ? "Great Job!" : "Keep Learning!"}
              </h3>
              <p className="text-sm text-muted-foreground">
                {feedback.isCorrect
                  ? "You demonstrated good understanding"
                  : "Let's work on improving your understanding"}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold gradient-text">{feedback.score}%</div>
            <p className="text-xs text-muted-foreground">Score</p>
          </div>
        </div>
      </div>

      <ScrollArea className="max-h-[500px]">
        <div className="p-6 space-y-6">
          {/* Explanation */}
          <div className="space-y-2">
            <h4 className="font-semibold flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-secondary" />
              Explanation
            </h4>
            <p className="text-muted-foreground leading-relaxed">
              {feedback.explanation}
            </p>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Strengths */}
            {feedback.analysis.strengths.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-green-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Strengths
                </h4>
                <ul className="space-y-2">
                  {feedback.analysis.strengths.map((strength, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-2 text-sm text-muted-foreground"
                    >
                      <ChevronRight className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {feedback.analysis.weaknesses.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-orange-400 flex items-center gap-2">
                  <XCircle className="w-4 h-4" />
                  Areas to Improve
                </h4>
                <ul className="space-y-2">
                  {feedback.analysis.weaknesses.map((weakness, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-2 text-sm text-muted-foreground"
                    >
                      <ChevronRight className="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" />
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Misconceptions */}
          {feedback.analysis.misconceptions.length > 0 && (
            <div className="space-y-3 p-4 rounded-lg bg-destructive/10 border border-destructive/20">
              <h4 className="font-semibold text-destructive flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                Misconceptions Identified
              </h4>
              <ul className="space-y-2">
                {feedback.analysis.misconceptions.map((misconception, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm"
                  >
                    <span className="text-destructive">•</span>
                    {misconception}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Improvement Plan */}
          <div className="space-y-4 p-4 rounded-lg bg-primary/5 border border-primary/20">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                Personalized Improvement Plan
              </h4>
              <Badge variant="secondary">
                ~{feedback.improvementPlan.estimatedTime} min
              </Badge>
            </div>

            {/* Target Concepts */}
            <div className="flex flex-wrap gap-2">
              {feedback.improvementPlan.targetConcepts.map((concept, index) => (
                <Badge
                  key={index}
                  variant="outline"
                  className="cursor-pointer hover:bg-primary/10"
                  onClick={() => onReviewConcept?.(concept)}
                >
                  {concept}
                </Badge>
              ))}
            </div>

            {/* Suggested Actions */}
            <div className="space-y-2">
              <p className="text-sm font-medium">Suggested Actions:</p>
              <ul className="space-y-2">
                {feedback.improvementPlan.suggestedActions.map((action, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-2 text-sm text-muted-foreground"
                  >
                    <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-xs text-primary">
                      {index + 1}
                    </div>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Resources */}
          {feedback.resources && feedback.resources.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-secondary" />
                Recommended Resources
              </h4>
              <div className="grid gap-2">
                {feedback.resources.map((resource) => (
                  <a
                    key={resource.id}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-lg border border-border/50 hover:bg-primary/5 transition-colors group"
                  >
                    <div className="w-10 h-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                      {getResourceIcon(resource.type)}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm group-hover:text-primary transition-colors">
                        {resource.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {resource.description}
                      </p>
                    </div>
                    <Badge variant="secondary">{resource.type}</Badge>
                  </a>
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
            <Progress value={feedback.score} className="w-32 h-2" />
            <span className="text-sm text-muted-foreground">Mastery Progress</span>
          </div>
          <Button onClick={onNextQuestion} className="gap-2">
            Next Question
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};
