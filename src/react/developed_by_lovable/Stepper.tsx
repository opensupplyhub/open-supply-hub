import { CheckCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface Step {
  id: string;
  title: string;
  icon: React.ReactNode;
  subtitle?: string;
  timeEstimate?: string;
}

interface StepperProps {
  steps: Step[];
  currentStep: string;
  completedSteps: string[];
  onStepClick: (stepId: string) => void;
}

export const Stepper = ({ steps, currentStep, completedSteps, onStepClick }: StepperProps) => {
  const currentIndex = steps.findIndex((step) => step.id === currentStep);

  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between relative">
        {/* Connection line */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" style={{ zIndex: 0 }} />
        
        {/* Active progress line */}
        <div 
          className="absolute top-5 left-0 h-0.5 bg-primary transition-all duration-300"
          style={{ 
            width: `${(currentIndex / (steps.length - 1)) * 100}%`,
            zIndex: 0
          }}
        />

        {/* Steps */}
        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(step.id);
          const isCurrent = step.id === currentStep;
          const isPast = index < currentIndex;

          return (
            <div
              key={step.id}
              className="flex flex-col items-center relative flex-1"
              style={{ zIndex: 1 }}
            >
              {/* Step marker */}
              <button
                onClick={() => onStepClick(step.id)}
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center transition-all",
                  "border-2 bg-background",
                  isCurrent && "border-primary bg-primary text-primary-foreground",
                  isCompleted && !isCurrent && "border-primary bg-primary text-primary-foreground",
                  !isCurrent && !isCompleted && "border-border text-muted-foreground hover:border-primary/50"
                )}
              >
                {isCompleted ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  step.icon
                )}
              </button>

              {/* Step label */}
              <div className="mt-2 text-center">
                <div className={cn(
                  "text-sm font-medium",
                  isCurrent && "text-foreground",
                  isCompleted && !isCurrent && "text-foreground",
                  !isCurrent && !isCompleted && "text-muted-foreground"
                )}>
                  {step.title}
                </div>
                {step.subtitle && (
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {step.subtitle}
                  </div>
                )}
                {step.timeEstimate && (
                  <div className={cn(
                    "text-xs mt-1 flex items-center justify-center gap-1 font-medium",
                    isCurrent && "text-primary",
                    isCompleted && !isCurrent && "text-primary",
                    !isCurrent && !isCompleted && "text-muted-foreground"
                  )}>
                    <Clock className="h-3 w-3" />
                    {step.timeEstimate}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
