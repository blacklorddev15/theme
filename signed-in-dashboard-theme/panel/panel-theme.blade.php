@extends('layouts.admin')
@section('title')
    Theme &amp; Branding
@endsection
@section('content-header')
    <h1>Theme &amp; Branding<small>Customize the company name, dashboard background, and accent colors.</small></h1>
    <ol class="breadcrumb">
        <li><a href="{{ route('admin.index') }}">Admin</a></li>
        <li class="active">Theme &amp; Branding</li>
    </ol>
@endsection
@section('content')
    <div class="row">
        <div class="col-xs-12 col-md-8">
            <div class="box box-primary">
                <div class="box-header with-border"><h3 class="box-title">Panel appearance</h3></div>
                <form action="{{ route('admin.theme.update') }}" method="POST">
                    {!! csrf_field() !!}
                    <div class="box-body">
                        <div class="form-group">
                            <label class="control-label" for="company_name">Company Name</label>
                            <input id="company_name" type="text" name="company_name" class="form-control" value="{{ old('company_name', $companyName) }}" maxlength="191" required>
                            <p class="text-muted"><small>Used in the signed-in panel header and Pterodactyl's Company Name setting.</small></p>
                        </div>
                        <div class="form-group">
                            <label class="control-label" for="background_url">Dashboard background image URL</label>
                            <input id="background_url" type="url" name="background_url" class="form-control" value="{{ old('background_url', $theme['backgroundUrl']) }}" placeholder="https://example.com/background.jpg">
                            <p class="text-muted"><small>Use an image URL beginning with http:// or https://. Leave blank to keep the current background.</small></p>
                        </div>
                        <div class="row">
                            <div class="form-group col-sm-6">
                                <label class="control-label" for="primary_color">Primary theme color</label>
                                <input id="primary_color" type="color" name="primary_color" class="form-control" style="height:42px;padding:3px" value="{{ old('primary_color', $theme['primaryColor']) }}" required>
                            </div>
                            <div class="form-group col-sm-6">
                                <label class="control-label" for="secondary_color">Secondary theme color</label>
                                <input id="secondary_color" type="color" name="secondary_color" class="form-control" style="height:42px;padding:3px" value="{{ old('secondary_color', $theme['secondaryColor']) }}" required>
                            </div>
                        </div>
                    </div>
                    <div class="box-footer">
                        <button type="submit" class="btn btn-primary pull-right">Save appearance</button>
                    </div>
                </form>
            </div>
        </div>
        <div class="col-xs-12 col-md-4">
            <div class="box">
                <div class="box-header with-border"><h3 class="box-title">About these settings</h3></div>
                <div class="box-body">
                    <p>The colors update the signed-in client and admin panel. The selected image is loaded by each viewer's browser.</p>
                    <p class="text-muted"><small>The existing login page is separate and is not changed by these controls.</small></p>
                </div>
            </div>
        </div>
    </div>
@endsection
