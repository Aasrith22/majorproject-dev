import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import {
  HelpCircle,
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Mic,
  Pencil,
  Type,
} from "lucide-react";
import type { GeneratedQuestion } from "@/types/api.types";
import { cn } from "@/lib/utils";

interface QuestionDisplayProps {
  question: GeneratedQuestion;
  onMultipleChoiceSelect?: (answer: string) => void;
}

export const QuestionDisplay = ({
  question,
  onMultipleChoiceSelect,
}: QuestionDisplayProps) => {
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [showHints, setShowHints] = useState(false);
  const [currentHintIndex, setCurrentHintIndex] = useState(0);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "medium":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "hard":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "";
    }
  };

  const getModalityIcon = () => {
    switch (question.expectedModality) {
      case "text":
        return <Type className="w-4 h-4" />;
      case "voice":
        return <Mic className="w-4 h-4" />;
      case "drawing":
        return <Pencil className="w-4 h-4" />;
      default:
        return <Type className="w-4 h-4" />;
    }
  };

  const handleOptionSelect = (value: string) => {
    setSelectedOption(value);
    onMultipleChoiceSelect?.(value);
  };

  const showNextHint = () => {
    if (question.hints && currentHintIndex < question.hints.length - 1) {
      setCurrentHintIndex((prev) => prev + 1);
    }
  };

  return (
    <Card className="glass-card p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <HelpCircle className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-semibold">Question</h3>
            <p className="text-xs text-muted-foreground">{question.topic}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={getDifficultyColor(question.difficulty)}>
            {question.difficulty}
          </Badge>
          <Badge variant="secondary" className="gap-1">
            {getModalityIcon()}
            {question.expectedModality}
          </Badge>
        </div>
      </div>

      {/* Question Content */}
      <div className="py-4">
        <p className="text-lg leading-relaxed">{question.content}</p>
      </div>

      {/* Multiple Choice Options */}
      {question.type === "multiple-choice" && question.options && (
        <RadioGroup
          value={selectedOption}
          onValueChange={handleOptionSelect}
          className="space-y-3"
        >
          {question.options.map((option, index) => (
            <div
              key={index}
              className={cn(
                "flex items-center space-x-3 p-4 rounded-lg border border-border/50 transition-all duration-200 cursor-pointer hover:bg-primary/5",
                selectedOption === option && "bg-primary/10 border-primary/50"
              )}
              onClick={() => handleOptionSelect(option)}
            >
              <RadioGroupItem value={option} id={`option-${index}`} />
              <Label
                htmlFor={`option-${index}`}
                className="flex-1 cursor-pointer"
              >
                {option}
              </Label>
            </div>
          ))}
        </RadioGroup>
      )}

      {/* Hints Section */}
      {question.hints && question.hints.length > 0 && (
        <div className="pt-4 border-t border-border/50">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowHints(!showHints)}
            className="gap-2 text-muted-foreground hover:text-foreground"
          >
            <Lightbulb className="w-4 h-4" />
            {showHints ? "Hide Hints" : "Need a Hint?"}
            {showHints ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </Button>

          {showHints && (
            <div className="mt-3 space-y-2 animate-slide-up">
              {question.hints.slice(0, currentHintIndex + 1).map((hint, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 p-3 rounded-lg bg-secondary/10 text-sm"
                >
                  <Lightbulb className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                  <span>{hint}</span>
                </div>
              ))}
              {currentHintIndex < question.hints.length - 1 && (
                <Button
                  variant="link"
                  size="sm"
                  onClick={showNextHint}
                  className="text-secondary"
                >
                  Show another hint ({question.hints.length - currentHintIndex - 1}{" "}
                  remaining)
                </Button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Expected Input Instruction */}
      <div className="pt-4 border-t border-border/50">
        <p className="text-sm text-muted-foreground flex items-center gap-2">
          {getModalityIcon()}
          {question.expectedModality === "text" &&
            "Type your answer in the text input below"}
          {question.expectedModality === "voice" &&
            "Use the voice recorder to speak your answer"}
          {question.expectedModality === "drawing" &&
            "Use the drawing canvas to illustrate your answer"}
          {question.expectedModality === "multimodal" &&
            "You can respond using text, voice, or drawing"}
        </p>
      </div>
    </Card>
  );
};
