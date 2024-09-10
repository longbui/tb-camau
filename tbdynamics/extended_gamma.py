from estival.priors import GammaPrior
import numpy as np
from scipy import stats
from scipy.optimize import minimize

class ExtendedGammaPrior(GammaPrior):
    @classmethod
    def from_median(
        cls,
        name: str,
        median: float,
        upper_ci: float,
        size: int = 1,
        tol=1e-6,
        max_eval=8,
        warn=False,
    ):
        def evaluate_gamma(params):
            k, theta = params[0], params[1]
            eval_median = stats.gamma.ppf(0.5, k, scale=theta)
            interval = stats.gamma.interval(0.95, k, scale=theta)
            return np.abs(eval_median - median) + np.abs(interval[1] - upper_ci)

        x = np.array((1.0, 1.0))
        cur_eval = 0
        loss = np.inf
        while (loss > tol) and (cur_eval < max_eval):
            res = minimize(
                evaluate_gamma, x, bounds=[(1e-8, np.inf), (1e-8, np.inf)], method="Nelder-Mead"
            )
            loss = evaluate_gamma(res.x) / upper_ci
            x = res.x
            cur_eval += 1

        if loss > tol:
            if warn:
                raise RuntimeWarning(
                    f"Loss of {loss} exceeds specified tolerance {tol}, parameters may be inaccurate"
                )

        return cls(name, x[0], x[1], size)
