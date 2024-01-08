/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * This code was autogenerated by RooClassFactory                            *
 *****************************************************************************/

#include "RooBWPS.h"

#include <Riostream.h>
#include <TMath.h>

ClassImp(RooBWPS);

RooBWPS::RooBWPS(const char *name, const char *title,
                 RooAbsReal &_x,
                 RooAbsReal &_mean,
                 RooAbsReal &_width,
                 RooAbsReal &_pt,
                 RooAbsReal &_temp)
    : RooAbsPdf(name, title),
      x("x", "x", this, _x),
      mean("mean", "mean", this, _mean),
      width("width", "width", this, _width),
      pt("pt", "pt", this, _pt),
      temp("temp", "temp", this, _temp)
{
}

RooBWPS::RooBWPS(const RooBWPS &other, const char *name)
    : RooAbsPdf(other, name), x("x", this, other.x), mean("mean", this, other.mean), width("width", this, other.width), pt("pt", this, other.pt), temp("temp", this, other.temp)
{
}

double RooBWPS::evaluate() const
{
  double arg = x - mean;
  double bw_only = 1 / (arg * arg + 0.25 * width * width);
  double mt = TMath::Sqrt(x * x + pt * pt);
  double ps_factor = x / mt * TMath::Exp(-mt / temp);
  return bw_only * ps_factor;
}