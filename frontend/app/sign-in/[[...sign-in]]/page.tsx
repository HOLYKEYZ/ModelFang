import { SignIn } from '@clerk/nextjs';

export default function Page() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <SignIn />
    </div>
  );
}
