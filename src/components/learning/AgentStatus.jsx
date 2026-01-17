import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  Brain,
  HelpCircle,
  MessageSquare,
  CheckCircle2,
  Loader2,
  Clock,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Configuration for each agent type
 */
const agentConfig = {
  "query-analysis": {
    name: "Query Analysis",
    icon: Brain,
    description: "Understanding your intent and context",
  },
  "information-retrieval": {
    name: "Information Retrieval",
    icon: Search,
    description: "Finding relevant learning materials",
  },
  "question-generation": {
    name: "Question Generation",
    icon: HelpCircle,
    description: "Creating adaptive assessment questions",
  },
  feedback: {
    name: "Feedback",
    icon: MessageSquare,
    description: "Analyzing response and generating feedback",
  },
};

const statusColors = {
  pending: "text-muted-foreground",
  processing: "text-secondary animate-pulse",
  completed: "text-green-400",
  error: "text-destructive",
  failed: "text-destructive",
};

const statusIcons = {
  pending: Clock,
  processing: Loader2,
  completed: CheckCircle2,
  error: Clock,
  failed: Clock,
};

/**
 * Display the status of AI agents in the learning workflow
 * @param {Object} props
 * @param {Array} props.agentResponses - Array of agent response objects
 * @param {boolean} props.isCompact - Whether to show compact view
 */
export const AgentStatus = ({ agentResponses, isCompact = false }) => {
  if (isCompact) {
    return (
      <div className="flex items-center gap-2">
        {agentResponses.map((response, index) => {
          const config = agentConfig[response.agentType];
          const Icon = config.icon;

          return (
            <div key={response.agentType} className="flex items-center">
              <div
                className={cn(
                  "relative w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                  response.status === "pending" && "border-muted bg-muted/20",
                  response.status === "processing" &&
                    "border-secondary bg-secondary/20",
                  response.status === "completed" &&
                    "border-green-400 bg-green-400/20",
                  response.status === "error" &&
                    "border-destructive bg-destructive/20"
                )}
                title={`${config.name}: ${response.status}`}
              >
                <Icon
                  className={cn("w-4 h-4", statusColors[response.status])}
                />
                {response.status === "processing" && (
                  <div className="absolute inset-0 rounded-full border-2 border-secondary border-t-transparent animate-spin" />
                )}
              </div>
              {index < agentResponses.length - 1 && (
                <ArrowRight className="w-4 h-4 mx-1 text-muted-foreground" />
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <Card className="glass-card p-4">
      <h4 className="font-semibold mb-4 flex items-center gap-2">
        <Brain className="w-4 h-4 text-primary" />
        AI Agent Workflow
      </h4>
      <div className="space-y-3">
        {agentResponses.map((response, index) => {
          const config = agentConfig[response.agentType];
          if (!config) return null; // Guard against unknown agent types
          const Icon = config.icon;
          const StatusIcon = statusIcons[response.status] || Clock; // Default to Clock if status not found

          return (
            <div key={response.agentType}>
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "relative w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-300",
                    response.status === "pending" &&
                      "border-muted bg-muted/20",
                    response.status === "processing" &&
                      "border-secondary bg-secondary/20",
                    response.status === "completed" &&
                      "border-green-400 bg-green-400/20",
                    response.status === "error" &&
                      "border-destructive bg-destructive/20"
                  )}
                >
                  <Icon
                    className={cn(
                      "w-5 h-5",
                      statusColors[response.status],
                      response.status === "processing" && "animate-pulse"
                    )}
                  />
                  {response.status === "processing" && (
                    <div className="absolute inset-0 rounded-xl border-2 border-secondary border-t-transparent animate-spin" />
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-sm">{config.name}</p>
                    <Badge
                      variant={
                        response.status === "completed"
                          ? "default"
                          : response.status === "processing"
                          ? "secondary"
                          : "outline"
                      }
                      className={cn(
                        "text-xs",
                        response.status === "completed" &&
                          "bg-green-500/20 text-green-400 border-green-500/30",
                        response.status === "processing" &&
                          "bg-secondary/20 text-secondary"
                      )}
                    >
                      <StatusIcon
                        className={cn(
                          "w-3 h-3 mr-1",
                          response.status === "processing" && "animate-spin"
                        )}
                      />
                      {response.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {config.description}
                  </p>
                  {response.processingTime && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Completed in {response.processingTime}ms
                    </p>
                  )}
                </div>
              </div>

              {/* Connector line */}
              {index < agentResponses.length - 1 && (
                <div className="flex items-center ml-5 my-1">
                  <div
                    className={cn(
                      "w-0.5 h-4",
                      response.status === "completed"
                        ? "bg-green-400/50"
                        : "bg-muted"
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};
