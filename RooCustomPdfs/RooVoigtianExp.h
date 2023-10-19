#ifndef ROO_VOIGTIAN_EXP
#define ROO_VOIGTIAN_EXP

#include <RooAbsPdf.h>
#include <RooRealProxy.h>

class RooVoigtianExp : public RooAbsPdf
{
public:
  RooVoigtianExp() {}
  RooVoigtianExp(const char *name, const char *title,
                 RooAbsReal &_x, RooAbsReal &_mean,
                 RooAbsReal &_width, RooAbsReal &_sigma, RooAbsReal &_tau,
                 bool doFast = false);
  RooVoigtianExp(const RooVoigtianExp &other, const char *name = nullptr);
  TObject *clone(const char *newname) const override { return new RooVoigtianExp(*this, newname); }
  inline virtual ~RooVoigtianExp() { }

  /// Enable the fast evaluation of the complex error function using look-up
  /// tables (default is the "slow" CERNlib algorithm).
  inline void selectFastAlgorithm() { _doFast = true; }

  /// Disable the fast evaluation of the complex error function using look-up
  /// tables (default is the "slow" CERNlib algorithm).
  inline void selectDefaultAlgorithm() { _doFast = false; }

protected:
  RooRealProxy x;
  RooRealProxy mean;
  RooRealProxy width;
  RooRealProxy sigma;
  RooRealProxy tau;

  double evaluate() const override;

private:
  bool _doFast = false;
  ClassDefOverride(RooVoigtianExp, 1)
};

#endif
