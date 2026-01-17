import { Navbar } from "./Navbar";
import { Footer } from "@/components/Footer";

/**
 * Main application layout wrapper
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child components
 * @param {boolean} props.showFooter - Whether to show footer (default: true)
 */
export const AppLayout = ({ children, showFooter = true }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 pt-16">{children}</main>
      {showFooter && <Footer />}
    </div>
  );
};
