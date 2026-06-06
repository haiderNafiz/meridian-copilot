export function createStageTimer() {
  const start = Date.now();
  let last = start;

  return {
    mark: (stage) => {
      const now = Date.now();
      const delta = now - last;
      last = now;

      return {
        stage,
        durationMs: delta
      };
    }
  };
}