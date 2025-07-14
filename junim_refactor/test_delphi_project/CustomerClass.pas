unit CustomerClass;

interface

uses
  SysUtils, Classes;

type
  TCustomer = class
  private
    FID: Integer;
    FName: string;
    FEmail: string;
    FPhone: string;
    FActive: Boolean;
    FCreatedDate: TDateTime;
    
  public
    constructor Create;
    destructor Destroy; override;
    
    property ID: Integer read FID write FID;
    property Name: string read FName write FName;
    property Email: string read FEmail write FEmail;
    property Phone: string read FPhone write FPhone;
    property Active: Boolean read FActive write FActive;
    property CreatedDate: TDateTime read FCreatedDate write FCreatedDate;
    
    function IsValid: Boolean;
    procedure Clear;
    function GetDisplayName: string;
    function CalculateScore: Double;
  end;

implementation

uses
  Utils;

constructor TCustomer.Create;
begin
  inherited Create;
  Clear;
end;

destructor TCustomer.Destroy;
begin
  inherited Destroy;
end;

function TCustomer.IsValid: Boolean;
begin
  Result := (Trim(FName) <> '') and 
           (Trim(FEmail) <> '') and
           IsValidEmail(FEmail);
end;

procedure TCustomer.Clear;
begin
  FID := 0;
  FName := '';
  FEmail := '';
  FPhone := '';
  FActive := True;
  FCreatedDate := Now;
end;

function TCustomer.GetDisplayName: string;
begin
  if Trim(FName) <> '' then
    Result := FName
  else
    Result := 'Cliente #' + IntToStr(FID);
end;

function TCustomer.CalculateScore: Double;
var
  Score: Double;
begin
  Score := 0;
  
  // Base score
  Score := Score + 10;
  
  // Name bonus
  if Length(Trim(FName)) > 3 then
    Score := Score + 5;
    
  // Email bonus
  if IsValidEmail(FEmail) then
    Score := Score + 10;
    
  // Phone bonus
  if Trim(FPhone) <> '' then
    Score := Score + 5;
    
  // Active bonus
  if FActive then
    Score := Score + 20;
    
  Result := Score;
end;

end.
