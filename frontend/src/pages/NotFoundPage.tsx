import { Link } from "react-router";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <h1 className="text-6xl font-bold text-primary">404</h1>
      <p className="text-base-content/60">Page not found</p>
      <Link to="/" className="btn btn-primary">
        Go home
      </Link>
    </div>
  );
}
