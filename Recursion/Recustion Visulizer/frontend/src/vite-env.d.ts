/// <reference types="vite/client" />

interface Window {
  MonacoEnvironment?: {
    getWorker(workerId: string, label: string): Worker;
  };
}

declare module "*?worker" {
  const WorkerFactory: new () => Worker;
  export default WorkerFactory;
}
