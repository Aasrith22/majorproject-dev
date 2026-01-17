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
  ListChecks,
  TextCursorInput,
  FileText,
  Send,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Display a learning question with various types (MCQ, fill-in-blank, essay)
 * @param {Object} props
 * @param {Object} props.question - The question object
 * @param {Function} props.onMultipleChoiceSelect - Callback when MCQ option selected
 * @param {Function} props.onSubmit - Callback when answer submitted
 * @param {boolean} props.isSubmitting - Whether submission is in progress
 */
export const QuestionDisplay = ({
  question,
  onMultipleChoiceSelect,
  onSubmit,
  isSubmitting = false,
}) => {
  const [selectedOption, setSelectedOption] = useState(null); // { id, text }
  const [showHints, setShowHints] = useState(false);
  const [currentHintIndex, setCurrentHintIndex] = useState(0);

  const handleMCQSubmit = () => {
    if (selectedOption && onSubmit) {
      // Pass the option ID as the third parameter (selectedOptionId)
      onSubmit(selectedOption.text, "text", selectedOption.id);
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

  const getQuestionTypeIcon = () => {
    switch (question.type) {
      case "multiple-choice":
        return <ListChecks className="w-4 h-4" />;
      case "fill-in-blank":
        return <TextCursorInput className="w-4 h-4" />;
      case "essay":
        return <FileText className="w-4 h-4" />;
      default:
        return <Type className="w-4 h-4" />;
    }
  };

  const getQuestionTypeLabel = () => {
    switch (question.type) {
      case "multiple-choice":
        return "MCQ";
      case "fill-in-blank":
        return "Fill in Blank";
      case "essay":
        return "Essay";
      case "short-answer":
        return "Short Answer";
      default:
        return question.type;
    }
  };

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    onMultipleChoiceSelect?.(option.id);
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
          <Badge variant="secondary" className="gap-1">
            {getQuestionTypeIcon()}
            {getQuestionTypeLabel()}
          </Badge>
        </div>
      </div>

      {/* Question Content */}
      <div className="py-4">
        <p className="text-lg leading-relaxed">{question.content}</p>
      </div>

      {/* Multiple Choice Options */}
      {question.type === "multiple-choice" && question.options && (
        <div className="space-y-4">
          <RadioGroup
            value={selectedOption?.id || ""}
            onValueChange={(id) => {
              const option = question.options.find(o => o.id === id);
              if (option) handleOptionSelect(option);
            }}
            className="space-y-3"
          >
            {question.options.map((option, index) => {
              // Handle both { id, text } objects and plain strings
              const optionId = option.id || String.fromCharCode(65 + index);
              const optionText = option.text || option;
              const isSelected = selectedOption?.id === optionId;
              
              return (
                <div
                  key={optionId}
                  className={cn(
                    "flex items-center space-x-3 p-4 rounded-lg border border-border/50 transition-all duration-200 cursor-pointer hover:bg-primary/5",
                    isSelected && "bg-primary/10 border-primary/50"
                  )}
                  onClick={() => handleOptionSelect({ id: optionId, text: optionText })}
                >
                  <RadioGroupItem value={optionId} id={`option-${optionId}`} />
                  <Label
                    htmlFor={`option-${optionId}`}
                    className="flex-1 cursor-pointer"
                  >
                    <span className="font-semibold text-primary mr-2">{optionId}.</span>
                    {optionText}
                  </Label>
                </div>
              );
            })}
          </RadioGroup>
          
          {/* MCQ Submit Button */}
          <div className="flex justify-end pt-2">
            <Button
              onClick={handleMCQSubmit}
              disabled={!selectedOption || isSubmitting}
              className="gap-2"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit Answer
            </Button>
          </div>
        </div>
      )}

      {/* Fill in the Blank Instructions */}
      {question.type === "fill-in-blank" && (
        <div className="py-2 px-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
          <p className="text-sm text-purple-400 flex items-center gap-2">
            <TextCursorInput className="w-4 h-4" />
            Fill in the blank{question.blanks && question.blanks > 1 ? "s" : ""} with the correct answer
          </p>
        </div>
      )}

      {/* Essay Instructions */}
      {question.type === "essay" && (
        <div className="py-2 px-4 rounded-lg bg-green-500/10 border border-green-500/20">
          <p className="text-sm text-green-400 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Write a detailed essay response. Explain your reasoning clearly and provide examples where appropriate.
          </p>
        </div>
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

      {/* Expected Input Instruction - Only show for non-MCQ */}
      {question.type !== "multiple-choice" && (
        <div className="pt-4 border-t border-border/50">
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            {getModalityIcon()}
            {question.type === "fill-in-blank" &&
              "Type your answer in the input field below"}
            {question.type === "essay" &&
              "Write your detailed response in the text area below"}
            {question.type === "short-answer" &&
              "Type a brief answer in the input field below"}
          </p>
        </div>
      )}
    </Card>
  );
};
