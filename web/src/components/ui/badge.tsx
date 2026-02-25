import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground hover:bg-primary/80 shadow-sm hover:shadow-md",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-sm hover:shadow-md",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80 shadow-sm hover:shadow-md animate-pulse-glow",
        outline: "text-foreground hover:bg-accent hover:shadow-sm",
        success: "border-transparent bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-sm hover:shadow-md hover:scale-105",
        warning: "border-transparent bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm hover:shadow-md hover:scale-105",
        critical: "border-transparent bg-gradient-to-r from-rose-500 to-red-500 text-white shadow-sm hover:shadow-lg hover:scale-105 animate-pulse-glow",
        glass: "glass hover:shadow-md",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  pulse?: boolean
}

function Badge({ className, variant, pulse = false, ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        badgeVariants({ variant }),
        pulse && "animate-pulse",
        "hover:scale-105 active:scale-95 cursor-pointer",
        className
      )}
      {...props}
    />
  )
}
export { Badge, badgeVariants }
