unit Utils;

interface

uses
  SysUtils, Classes, RegularExpressions;

function IsValidEmail(const Email: string): Boolean;
function FormatCurrency(const Value: Double): string;
function ValidateRequired(const Value: string; const FieldName: string): Boolean;
function CleanPhoneNumber(const Phone: string): string;
function GenerateID: string;
procedure LogError(const ErrorMsg: string);
procedure LogInfo(const InfoMsg: string);

implementation

function IsValidEmail(const Email: string): Boolean;
var
  EmailRegex: TRegEx;
begin
  EmailRegex := TRegEx.Create('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
  Result := EmailRegex.IsMatch(Email);
end;

function FormatCurrency(const Value: Double): string;
begin
  Result := FormatFloat('#,##0.00', Value);
end;

function ValidateRequired(const Value: string; const FieldName: string): Boolean;
begin
  Result := Trim(Value) <> '';
  if not Result then
    raise Exception.Create(FieldName + ' é obrigatório');
end;

function CleanPhoneNumber(const Phone: string): string;
var
  I: Integer;
begin
  Result := '';
  for I := 1 to Length(Phone) do
  begin
    if CharInSet(Phone[I], ['0'..'9']) then
      Result := Result + Phone[I];
  end;
end;

function GenerateID: string;
begin
  Result := FormatDateTime('yyyymmddhhnnsszzz', Now);
end;

procedure LogError(const ErrorMsg: string);
var
  LogFile: TextFile;
  LogFileName: string;
begin
  try
    LogFileName := ExtractFilePath(ParamStr(0)) + 'error.log';
    AssignFile(LogFile, LogFileName);
    
    if FileExists(LogFileName) then
      Append(LogFile)
    else
      Rewrite(LogFile);
      
    Writeln(LogFile, FormatDateTime('yyyy-mm-dd hh:nn:ss', Now) + ' ERROR: ' + ErrorMsg);
    CloseFile(LogFile);
    
  except
    // Silent fail - don't want logging errors to crash the app
  end;
end;

procedure LogInfo(const InfoMsg: string);
var
  LogFile: TextFile;
  LogFileName: string;
begin
  try
    LogFileName := ExtractFilePath(ParamStr(0)) + 'info.log';
    AssignFile(LogFile, LogFileName);
    
    if FileExists(LogFileName) then
      Append(LogFile)
    else
      Rewrite(LogFile);
      
    Writeln(LogFile, FormatDateTime('yyyy-mm-dd hh:nn:ss', Now) + ' INFO: ' + InfoMsg);
    CloseFile(LogFile);
    
  except
    // Silent fail
  end;
end;

end.
