unit DataModule;

interface

uses
  SysUtils, Classes, DB, ADODB, CustomerClass;

type
  TdmMain = class(TDataModule)
    Connection: TADOConnection;
    qryCustomers: TADOQuery;
    dsCustomers: TDataSource;
    qryTemp: TADOQuery;
    
    procedure DataModuleCreate(Sender: TObject);
    procedure DataModuleDestroy(Sender: TObject);
    
  private
    { Private declarations }
    
  public
    { Public declarations }
    procedure InsertCustomer(Customer: TCustomer);
    procedure UpdateCustomer(Customer: TCustomer);
    procedure DeleteCustomer(CustomerID: Integer);
    function GetCustomerByID(CustomerID: Integer): TCustomer;
    function GetActiveCustomers: TADOQuery;
    procedure BeginTransaction;
    procedure CommitTransaction;
    procedure RollbackTransaction;
  end;

var
  dmMain: TdmMain;

implementation

{$R *.dfm}

procedure TdmMain.DataModuleCreate(Sender: TObject);
begin
  try
    Connection.ConnectionString := 'Provider=SQLOLEDB;Data Source=localhost;' +
                                 'Initial Catalog=CustomerDB;Integrated Security=SSPI';
    Connection.Open;
    
    qryCustomers.Connection := Connection;
    qryCustomers.SQL.Clear;
    qryCustomers.SQL.Add('SELECT CustomerID, Name, Email, Phone, CreatedDate FROM Customers ORDER BY Name');
    
    dsCustomers.DataSet := qryCustomers;
    
  except
    on E: Exception do
      raise Exception.Create('Erro ao conectar com banco de dados: ' + E.Message);
  end;
end;

procedure TdmMain.DataModuleDestroy(Sender: TObject);
begin
  if Connection.Connected then
    Connection.Close;
end;

procedure TdmMain.InsertCustomer(Customer: TCustomer);
begin
  try
    qryTemp.Close;
    qryTemp.SQL.Clear;
    qryTemp.SQL.Add('INSERT INTO Customers (Name, Email, Phone, CreatedDate) ');
    qryTemp.SQL.Add('VALUES (:Name, :Email, :Phone, :CreatedDate)');
    
    qryTemp.Parameters.ParamByName('Name').Value := Customer.Name;
    qryTemp.Parameters.ParamByName('Email').Value := Customer.Email;
    qryTemp.Parameters.ParamByName('Phone').Value := Customer.Phone;
    qryTemp.Parameters.ParamByName('CreatedDate').Value := Now;
    
    qryTemp.ExecSQL;
    
  except
    on E: Exception do
      raise Exception.Create('Erro ao inserir cliente: ' + E.Message);
  end;
end;

procedure TdmMain.UpdateCustomer(Customer: TCustomer);
begin
  try
    qryTemp.Close;
    qryTemp.SQL.Clear;
    qryTemp.SQL.Add('UPDATE Customers SET ');
    qryTemp.SQL.Add('Name = :Name, Email = :Email, Phone = :Phone ');
    qryTemp.SQL.Add('WHERE CustomerID = :CustomerID');
    
    qryTemp.Parameters.ParamByName('Name').Value := Customer.Name;
    qryTemp.Parameters.ParamByName('Email').Value := Customer.Email;
    qryTemp.Parameters.ParamByName('Phone').Value := Customer.Phone;
    qryTemp.Parameters.ParamByName('CustomerID').Value := Customer.ID;
    
    qryTemp.ExecSQL;
    
  except
    on E: Exception do
      raise Exception.Create('Erro ao atualizar cliente: ' + E.Message);
  end;
end;

procedure TdmMain.DeleteCustomer(CustomerID: Integer);
begin
  try
    qryTemp.Close;
    qryTemp.SQL.Clear;
    qryTemp.SQL.Add('DELETE FROM Customers WHERE CustomerID = :CustomerID');
    qryTemp.Parameters.ParamByName('CustomerID').Value := CustomerID;
    qryTemp.ExecSQL;
    
  except
    on E: Exception do
      raise Exception.Create('Erro ao excluir cliente: ' + E.Message);
  end;
end;

function TdmMain.GetCustomerByID(CustomerID: Integer): TCustomer;
begin
  Result := nil;
  
  try
    qryTemp.Close;
    qryTemp.SQL.Clear;
    qryTemp.SQL.Add('SELECT CustomerID, Name, Email, Phone FROM Customers ');
    qryTemp.SQL.Add('WHERE CustomerID = :CustomerID');
    qryTemp.Parameters.ParamByName('CustomerID').Value := CustomerID;
    qryTemp.Open;
    
    if not qryTemp.Eof then
    begin
      Result := TCustomer.Create;
      Result.ID := qryTemp.FieldByName('CustomerID').AsInteger;
      Result.Name := qryTemp.FieldByName('Name').AsString;
      Result.Email := qryTemp.FieldByName('Email').AsString;
      Result.Phone := qryTemp.FieldByName('Phone').AsString;
    end;
    
  except
    on E: Exception do
      raise Exception.Create('Erro ao buscar cliente: ' + E.Message);
  end;
end;

function TdmMain.GetActiveCustomers: TADOQuery;
begin
  qryTemp.Close;
  qryTemp.SQL.Clear;
  qryTemp.SQL.Add('SELECT CustomerID, Name, Email, Phone FROM Customers ');
  qryTemp.SQL.Add('WHERE Active = 1 ORDER BY Name');
  qryTemp.Open;
  Result := qryTemp;
end;

procedure TdmMain.BeginTransaction;
begin
  Connection.BeginTrans;
end;

procedure TdmMain.CommitTransaction;
begin
  Connection.CommitTrans;
end;

procedure TdmMain.RollbackTransaction;
begin
  Connection.RollbackTrans;
end;

end.
