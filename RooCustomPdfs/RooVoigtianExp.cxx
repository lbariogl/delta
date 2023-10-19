#include "RooVoigtianExp.h"

#include <RooMath.h>
#include <RooBatchCompute.h>

#include <cmath>
#include <complex>

ClassImp(RooVoigtianExp);

////////////////////////////////////////////////////////////////////////////////
/// Construct a RooVoigtianExp PDF, which represents the convolution of a
/// Breit-Wigner with a Gaussian.
/// \param name Name that identifies the PDF in computations.
/// \param title Title for plotting.
/// \param _x The observable for the PDF.
/// \param _mean The mean of the distribution.
/// \param _width The **full width at half maximum (FWHM)** of the Breit-Wigner
///               (often referred to as \f$\Gamma\f$ or \f$2\gamma\f$).
/// \param _sigma The width of the Gaussian distribution.
/// \param _tau The slope of the exponential tail.
/// \param doFast Use the faster look-up-table-based method for the evaluation
///               of the complex error function.

RooVoigtianExp::RooVoigtianExp(const char *name, const char *title,
                               RooAbsReal &_x, RooAbsReal &_mean,
                               RooAbsReal &_width, RooAbsReal &_sigma, RooAbsReal &_tau,
                               bool doFast) : RooAbsPdf(name, title),
                                              x("x", "Dependent", this, _x),
                                              mean("mean", "Mean", this, _mean),
                                              width("width", "Breit-Wigner Width", this, _width),
                                              sigma("sigma", "Gauss Width", this, _sigma),
                                              tau("tau", "Exponential slope", this, _tau),
                                              _doFast(doFast)
{
}

////////////////////////////////////////////////////////////////////////////////

RooVoigtianExp::RooVoigtianExp(const RooVoigtianExp &other, const char *name) : RooAbsPdf(other, name),
                                                                                x("x", this, other.x),
                                                                                mean("mean", this, other.mean),
                                                                                width("width", this, other.width),
                                                                                sigma("sigma", this, other.sigma),
                                                                                tau("tau", this, other.tau),
                                                                                _doFast(other._doFast)
{
}

////////////////////////////////////////////////////////////////////////////////

double RooVoigtianExp::evaluate() const
{
  double s = (sigma > 0) ? sigma : -sigma;
  double w = (width > 0) ? width : -width;

  double coef = -0.5 / (s * s);
  double arg = x - mean;

  // return constant for zero width and sigma
  if (s == 0. && w == 0.)
    return 1.;

  // Breit-Wigner for zero sigma
  if (s == 0.)
    return (1. / (arg * arg + 0.25 * w * w));

  // Gauss for zero width
  if (w == 0.)
    return std::exp(coef * arg * arg);

  // actual Voigtian for non-trivial width and sigma
  double c = 1. / (sqrt(2.) * s);
  double a = 0.5 * c * w;
  double u = c * arg;
  std::complex<double> z(u, a);
  std::complex<double> v(0.);

  if (u > tau)
  {
    return std::exp(-tau * (sqrt(2.) * u - 0.5 * tau));
  }

  if (_doFast)
  {
    v = RooMath::faddeeva_fast(z);
  }
  else
  {
    v = RooMath::faddeeva(z);
  }
  return c * v.real();
}
