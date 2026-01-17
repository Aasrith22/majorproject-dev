import { useState, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Send,
  Mic,
  MicOff,
  Pencil,
  Type,
  Loader2,
  Trash2,
  RotateCcw,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Multimodal input component supporting text, voice, and drawing inputs
 * @param {Object} props
 * @param {Function} props.onSubmit - Callback when input submitted (content, modality, rawData)
 * @param {boolean} props.isLoading - Whether submission is in progress
 * @param {boolean} props.disabled - Whether input is disabled
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.questionType - Type of question (fill-in-blank, essay, etc.)
 */
export const MultimodalInput = ({
  onSubmit,
  isLoading = false,
  disabled = false,
  placeholder = "Type your answer or question here...",
  questionType,
}) => {
  const [activeTab, setActiveTab] = useState("text");
  const [textInput, setTextInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);

  // Determine the appropriate placeholder based on question type
  const getPlaceholder = () => {
    if (questionType === "fill-in-blank") {
      return "Type the word(s) to fill in the blank...";
    }
    if (questionType === "essay") {
      return "Write your detailed essay response here. Explain your reasoning and provide examples...";
    }
    if (questionType === "multiple-choice") {
      return "You can also type your answer here...";
    }
    return placeholder;
  };

  // Check if we should show simplified input for fill-in-blank
  const isFillInBlank = questionType === "fill-in-blank";
  const isEssay = questionType === "essay";
  
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);
  const isDrawingRef = useRef(false);
  const lastPosRef = useRef({ x: 0, y: 0 });

  // Text Input Handlers
  const handleTextSubmit = () => {
    if (textInput.trim() && !isLoading) {
      onSubmit(textInput.trim(), "text");
      setTextInput("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleTextSubmit();
    }
  };

  // Voice Recording Handlers
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setAudioBlob(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const handleVoiceSubmit = async () => {
    if (audioBlob) {
      // Convert to base64 for transmission
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = () => {
        const base64 = reader.result;
        onSubmit("Voice input submitted", "voice", base64);
        setAudioBlob(null);
        setRecordingTime(0);
      };
    }
  };

  const clearRecording = () => {
    setAudioBlob(null);
    setRecordingTime(0);
  };

  // Drawing Canvas Handlers
  const initCanvas = useCallback((canvas) => {
    if (canvas) {
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#1a1a2e";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
      }
    }
  }, []);

  const getCanvasPosition = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if (e.touches) {
      const touch = e.touches[0];
      return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY,
      };
    }

    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const startDrawing = (e) => {
    isDrawingRef.current = true;
    const pos = getCanvasPosition(e);
    lastPosRef.current = pos;
  };

  const draw = (e) => {
    if (!isDrawingRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!ctx) return;

    const pos = getCanvasPosition(e);

    ctx.beginPath();
    ctx.moveTo(lastPosRef.current.x, lastPosRef.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();

    lastPosRef.current = pos;
  };

  const stopDrawing = () => {
    isDrawingRef.current = false;
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#1a1a2e";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  const handleDrawingSubmit = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const dataUrl = canvas.toDataURL("image/png");
      onSubmit("Drawing submitted", "drawing", dataUrl);
      clearCanvas();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // For fill-in-blank and essay, show simplified UI without tabs
  if (isFillInBlank) {
    return (
      <Card className="glass-card p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-purple-400">
            <Type className="w-4 h-4" />
            <span className="text-sm font-medium">Fill in the Blank</span>
          </div>
          <Input
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={getPlaceholder()}
            disabled={disabled || isLoading}
            className="bg-background/50 text-lg"
            autoFocus
          />
          <div className="flex justify-end">
            <Button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isLoading || disabled}
              className="gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit Answer
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  if (isEssay) {
    return (
      <Card className="glass-card p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-green-400">
            <Type className="w-4 h-4" />
            <span className="text-sm font-medium">Essay Response</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Write a comprehensive response. Consider structure, examples, and clear explanations.
          </p>
          <Textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder={getPlaceholder()}
            disabled={disabled || isLoading}
            className="min-h-[250px] resize-none bg-background/50"
            autoFocus
          />
          <div className="flex justify-between items-center">
            <p className="text-xs text-muted-foreground">
              {textInput.length} characters | ~{Math.ceil(textInput.split(/\s+/).filter(w => w).length)} words
            </p>
            <Button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isLoading || disabled}
              className="gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit Essay
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  // Default: show full multimodal input with tabs (for other question types)
  return (
    <Card className="glass-card p-4">
      <Tabs
        value={activeTab}
        onValueChange={(v) => setActiveTab(v)}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-3 mb-4">
          <TabsTrigger value="text" className="gap-2">
            <Type className="w-4 h-4" />
            Text
          </TabsTrigger>
          <TabsTrigger value="voice" className="gap-2">
            <Mic className="w-4 h-4" />
            Voice
          </TabsTrigger>
          <TabsTrigger value="drawing" className="gap-2">
            <Pencil className="w-4 h-4" />
            Drawing
          </TabsTrigger>
        </TabsList>

        {/* Text Input */}
        <TabsContent value="text" className="space-y-4">
          <Textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={getPlaceholder()}
            disabled={disabled || isLoading}
            className="min-h-[120px] resize-none bg-background/50"
          />
          <div className="flex justify-end">
            <Button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isLoading || disabled}
              className="gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit
            </Button>
          </div>
        </TabsContent>

        {/* Voice Input */}
        <TabsContent value="voice" className="space-y-4">
          <div className="flex flex-col items-center justify-center py-8 space-y-6">
            <div
              className={cn(
                "w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300",
                isRecording
                  ? "bg-destructive/20 animate-pulse"
                  : audioBlob
                  ? "bg-primary/20"
                  : "bg-muted"
              )}
            >
              {isRecording ? (
                <MicOff className="w-10 h-10 text-destructive" />
              ) : (
                <Mic
                  className={cn(
                    "w-10 h-10",
                    audioBlob ? "text-primary" : "text-muted-foreground"
                  )}
                />
              )}
            </div>

            <div className="text-center">
              {isRecording ? (
                <div className="space-y-2">
                  <p className="text-lg font-semibold text-destructive">
                    Recording...
                  </p>
                  <p className="text-2xl font-mono">{formatTime(recordingTime)}</p>
                </div>
              ) : audioBlob ? (
                <div className="space-y-2">
                  <p className="text-lg font-semibold text-primary">
                    Recording Complete
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Duration: {formatTime(recordingTime)}
                  </p>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  Click the button below to start recording
                </p>
              )}
            </div>

            <div className="flex gap-3">
              {!audioBlob ? (
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  variant={isRecording ? "destructive" : "default"}
                  size="lg"
                  disabled={disabled}
                  className="gap-2"
                >
                  {isRecording ? (
                    <>
                      <MicOff className="w-5 h-5" />
                      Stop Recording
                    </>
                  ) : (
                    <>
                      <Mic className="w-5 h-5" />
                      Start Recording
                    </>
                  )}
                </Button>
              ) : (
                <>
                  <Button
                    onClick={clearRecording}
                    variant="outline"
                    className="gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Re-record
                  </Button>
                  <Button
                    onClick={handleVoiceSubmit}
                    disabled={isLoading}
                    className="gap-2"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    Submit
                  </Button>
                </>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Drawing Input */}
        <TabsContent value="drawing" className="space-y-4">
          <div className="relative">
            <canvas
              ref={(el) => {
                canvasRef.current = el;
                initCanvas(el);
              }}
              width={600}
              height={400}
              className="w-full h-[300px] rounded-lg border border-border cursor-crosshair touch-none"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchMove={draw}
              onTouchEnd={stopDrawing}
            />
            <p className="absolute bottom-2 left-2 text-xs text-muted-foreground bg-background/80 px-2 py-1 rounded">
              Draw your diagram or answer here
            </p>
          </div>
          <div className="flex justify-between">
            <Button onClick={clearCanvas} variant="outline" className="gap-2">
              <Trash2 className="w-4 h-4" />
              Clear
            </Button>
            <Button
              onClick={handleDrawingSubmit}
              disabled={isLoading || disabled}
              className="gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit Drawing
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  );
};
