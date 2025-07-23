unit SampleUnit;

interface

uses
  SysUtils, Classes, Forms, Controls, StdCtrls;

type
  TMainForm = class(TForm)
    btnCalculate: TButton;
    edtValue1: TEdit;
    edtValue2: TEdit;
    lblResult: TLabel;
    procedure btnCalculateClick(Sender: TObject);
  private
    FTotal: Double;
  public
    function CalculateSum(Value1, Value2: Double): Double;
    procedure ShowResult(const Result: Double);
  end;

var
  MainForm: TMainForm;

implementation

{$R *.dfm}

procedure TMainForm.btnCalculateClick(Sender: TObject);
var
  Val1, Val2, Result: Double;
begin
  try
    Val1 := StrToFloat(edtValue1.Text);
    Val2 := StrToFloat(edtValue2.Text);
    Result := CalculateSum(Val1, Val2);
    ShowResult(Result);
  except
    on E: Exception do
      ShowMessage('Erro no cálculo: ' + E.Message);
  end;
end;

function TMainForm.CalculateSum(Value1, Value2: Double): Double;
begin
  // Regra de negócio: soma simples com validação
  if (Value1 < 0) or (Value2 < 0) then
    raise Exception.Create('Valores devem ser positivos');
  
  Result := Value1 + Value2;
  FTotal := FTotal + Result;
end;

procedure TMainForm.ShowResult(const Result: Double);
begin
  lblResult.Caption := 'Resultado: ' + FloatToStr(Result);
end;

end.
