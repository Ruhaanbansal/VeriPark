import type { ButtonHTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "outline";
type Size = "md" | "lg" | "sm";

const base =
  "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[--color-navy]";

const variants: Record<Variant, string> = {
  primary: "bg-[--color-navy] text-white hover:bg-[--color-navy-dark] shadow-soft",
  secondary: "bg-[--color-teal-50] text-[--color-teal-dark] hover:bg-[--color-teal-100]",
  outline: "border border-[--color-border] bg-white text-[--color-navy] hover:bg-[--color-bg-off]",
  ghost: "text-[--color-navy] hover:bg-[--color-navy-50]",
};

const sizes: Record<Size, string> = {
  sm: "px-3.5 py-2 text-sm",
  md: "px-5 py-3 text-[15px]",
  lg: "px-6 py-4 text-base",
};

interface CommonProps {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
  className?: string;
  fullWidth?: boolean;
}

interface ButtonProps extends CommonProps, Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> {
  href?: undefined;
}

interface LinkButtonProps extends CommonProps {
  href: string;
}

export function Button(props: ButtonProps | LinkButtonProps) {
  const { variant = "primary", size = "md", children, className, fullWidth, ...rest } = props;
  const classes = cn(base, variants[variant], sizes[size], fullWidth && "w-full", className);

  if ("href" in props && props.href) {
    return (
      <Link href={props.href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  );
}
