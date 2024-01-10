#ifndef RooGausExp_hpp
#define RooGausExp_hpp

#include <RooAbsPdf.h>
#include <RooRealProxy.h>
#include <RooCategoryProxy.h>
#include <RooAbsReal.h>

#define _AN_INT_

class RooGausExp : public RooAbsPdf {
public:
  RooGausExp() {} ;
  RooGausExp(const char *name, const char *title,
          RooAbsReal& _x,
          RooAbsReal& _mu,
          RooAbsReal& _sig,
          RooAbsReal& _tau);
  RooGausExp(const RooGausExp& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooGausExp(*this,newname); }
  inline virtual ~RooGausExp() { }

#ifdef _AN_INT_
  virtual Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* r=0) const;
  virtual Double_t analyticalIntegral(Int_t code,const char* rangeName=0) const;
#endif
protected:
  double IntExp(double x,double tau) const;
  double IntGaus(double x) const;

  RooRealProxy x ;
  RooRealProxy mu ;
  RooRealProxy sig ;
  RooRealProxy tau ;

  double evaluate() const ;

private:

  ClassDef(RooGausExp,1)
};

#endif
