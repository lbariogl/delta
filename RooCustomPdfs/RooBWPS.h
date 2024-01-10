#ifndef RooBWHF_hpp
#define RooBWHF_hpp

#include <RooAbsPdf.h>
#include <RooRealProxy.h>
#include <RooCategoryProxy.h>
#include <RooAbsReal.h>

#define _AN_INT_

class RooBWPS : public RooAbsPdf
{
public:
  RooBWPS(){};
  RooBWPS(const char *name, const char *title,
          RooAbsReal &_x,
          RooAbsReal &_mean,
          RooAbsReal &_width,
          RooAbsReal &_pt,
          RooAbsReal &_temp);
  RooBWPS(const RooBWPS &other, const char *name = 0);
  virtual TObject *clone(const char *newname) const { return new RooBWPS(*this, newname); }
  inline virtual ~RooBWPS() {}

protected:

  RooRealProxy x;
  RooRealProxy mean;
  RooRealProxy width;
  RooRealProxy pt;
  RooRealProxy temp;

  double evaluate() const;

private:
  ClassDef(RooBWPS, 1)
};

#endif
